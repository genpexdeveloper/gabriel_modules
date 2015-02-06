from copy import deepcopy
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime

from openerp.tools.translate import _

from auto_vivification import AutoVivification
from ads_data import ads_data
from tools import parse_date

class ads_picking(ads_data):
    """
    Handles the processing of MVTS files to receive a purchase order or deliver a sales order
    """

    file_name_prefix = ['MVTS']
    xml_root = 'mvts'
    _auto_remove = False
    pre_process_errors = []

    def pre_process_hook(self, pool, cr):
        """ Lets us process self.data in batches per picking """
        self.data_from_xml = deepcopy(self.data)
        self.data = self._extract_to_process()
        return self.pre_process_errors

    def process(self, pool, cr, picking):
        """
        Triggers _process_picking to handle the processing of a PO or SO picking.

        @param pool: OpenERP object pool
        @param cr: OpenERP database cursor
        @param picking: The data for the picking to process. See _extract_to_process
        """
        # iterate over extracted data and call self._process_picking
        picking_name = picking.keys()[0]
        picking_lines = picking[picking_name]

        self._process_picking(pool, cr, picking_name, picking_lines)

        # remove all elements with NUMBL == picking_name from self.data_from_xml
        root_key = self.data_from_xml.keys()[0]
        self.data_from_xml[root_key] = [move for move in self.data_from_xml[root_key] if move['NUMBL'] != picking_name]

    def post_process_hook(self, pool, cr):
        """ Lets us process self.data in batches per picking """
        try:
            self.data = self.data_from_xml
            return []
        except Exception as e:
            return ['%s: %s' % (type(e), unicode(e))]

    def _extract_to_process(self):
        """
        Organises self.data into a batch of data that can be imported per picking.
        @return: {'Pickings': [{'picking_name': [{'product_code': .., 'quantity': .., 'date': ..}]]}
        """
        move_data = AutoVivification({'Pickings': []})
        root_key = self.data.keys()[0]

        for move in self.data[root_key]:

            # catch exception per data node and save it in self.post_process_errors to return up a level
            try:

                # extract data from self.data into move_data dict
                assert all([field in move and move[field] for field in ['TYPEMVT', 'CODEMVT', 'CODE_ART', 'QTE']]), \
                    _('This move has been skipped because it was missing a required field: %s' % move)

                picking_name = 'NUMBL' in move and move['NUMBL'] or ''

                # ignore MVTS without a num bl as they are manual corrections which are represented anyway in STOC files
                if not picking_name:
                    continue

                assert picking_name, _("Must have a picking name (NUMBL) for moves whose CODEMVT is not REG")

                move_type = move['TYPEMVT']
                move_type = move_type == 'E' and 'in' or 'out'

                product_code = str(move['CODE_ART'])
                quantity = move['QTE']
                move_date = 'DATEMVT' in move and move['DATEMVT']

                assert picking_name, _('Picking name (NUMBL field) must have a value for node %s') % move
                assert move['TYPEMVT'] in ['E', 'S'], _('Move type (TYPEMVT field) must be either E or S for picking %s') % picking_name
                assert product_code, _('Product code (CODE_ART field) must have a value for picking %s') % picking_name

                # if MVTS is for an OUT, quantity will be negative so make it positive
                if move_type == 'out':
                    quantity = quantity * -1

                line_vals = {'name': product_code, 'quantity': quantity, 'date': move_date, 'move_type': move_type}

                # try to find an existing list for picking_name. If found, append our data, otherwise create it
                target = [picking for picking in move_data['Pickings'] if picking.keys()[0] == picking_name]
                if not target:
                    move_data['Pickings'].append({picking_name: [line_vals]})
                else:
                    target[0][picking_name].append(line_vals)

            except Exception as e:
                self.pre_process_errors.append('%s: %s' % (type(e), unicode(e)))

        return move_data

    def _find_picking(self, pool, cr, picking_name):
        """
        Find's the most recent picking for an order. This will be the original picking
        if the picking has not been split, or the most recent split picking if it has.
        @return int: ID of the picking record
        """
        picking_obj = pool.get('stock.picking')
        picking = None
        backorder_ids = picking_obj.search(cr, 1, [('backorder_id', '=', picking_name), ('state','in',['assigned', 'confirmed', 'partially_available'])])

        while(backorder_ids):
            picking = picking_obj.browse(cr, 1, backorder_ids[0])
            backorder_ids = picking_obj.search(cr, 1, [('backorder_id', '=', picking.name), ('state','in',['assigned', 'confirmed', 'partially_available'])])

        if not picking:
            picking_ids = picking_obj.search(cr, 1, [('name', '=', picking_name), ('state','in',['assigned', 'partially_available'])])
            assert picking_ids, _("Could not find picking with name '%s' and state assigned or partially available" % picking_name)
            picking = picking_obj.browse(cr, 1, picking_ids[0])

        return picking.id

    def _process_picking(self, pool, cr, picking_name, picking_lines_original):
        """
        Executes the reception wizard for an IN or the delivery wizard for an out with
        data from self.data received from ADS
        @param pool: OpenERP object pool
        @param cursor cr: OpenERP database cursor
        @param str picking_name: Name of the picking to be processed
        @param list picking_lines: A list of picking move data. Refer to self._extract_to_process
        """
        # validate params and find picking
        if not picking_lines_original:
            return

        assert picking_name, _("A picking was received from ADS without a name, so we can't process it")
        picking_id = self._find_picking(pool, cr, picking_name)
        assert picking_id, _("No picking found with name %s" % picking_name)
        picking = pool.get('stock.picking').browse(cr, 1, picking_id)
        assert picking.state != 'done', _("Picking '%s' (%d) has already been closed" % (picking_name, picking_id))
        # create working copy of picking_lines_original in case original is needed intact higher in the stack
        picking_lines = deepcopy(picking_lines_original)

        # Set the transferred lines to available in the picking
        # The sorting of both lists is to ensure we work from high to low, so that when multiple order lines exist
        # for the same product, we don't accidentally ship 5 items for the line that only ordered 3 and then
        # fail to handle the shipping of 3 items since we need 5. This is now optional since we handle this,
        # see long comment that starts with "Scenario if e.g. 3 lines: Prod A, unavailable, ordered 3 + 2;
        # product B: available." below, but it does limit line splits so it's retained.
        picking_move_lines_sorted = sorted(picking.move_lines, key=lambda line: line.product_uom_qty, reverse=True)
        picking_lines_sorted = sorted(picking_lines, key=lambda line: line.get('quantity'), reverse=True)
        for line in picking_move_lines_sorted:
            # Call force_assign on line, taking accounts into account, creating new line if incomplete transfer
            product_ref = line.product_id.x_new_ref
            for picking_line in picking_lines_sorted:
                if not picking_line.get('quantity'):
                    continue
                if picking_line.get('name') == product_ref:
                    remainder = line.product_uom_qty - picking_line.get('quantity', 0)
                    # assert remainder >= 0, _("A picking was received from ADS with a larger amount of items than was ordered, so we can't process it.")
                    if remainder > 0:
                        line.split(line, remainder)
                    # Scenario if e.g. 3 lines: Prod A, unavailable, ordered 3 + 2; product B: available.
                    # Shipped: 2 items of prod A, which is 2nd line.
                    # First pass will split line 1 into 2 shipped, 1 backorder. Incoming line gets quantity reset to 0
                    # The backorder will contain 3 lines: Prod A, qty = 1; Prod A, qty = 2, Prod B.
                    # If now a new MVTS file comes in for the remaining 3 from wat used to be line 1, the backorder
                    # will be processed.
                    # First pass: line 1, qty=1, shipped. Incoming line gets quantity updated to 2.
                    # Second pass: line 2, qty= 2, shipped. Incoming line gets quantity reset to 0.
                    picking_line['quantity'] -= line.product_uom_qty
                    line.force_assign()
        assert not len([x for x in picking_lines_sorted if x.get('quantity')]), _("More items were shipped than were ordered. We can't process this")
        picking.action_assign()


        # create a wizard record for this picking
        context = {
            'active_model': 'stock.picking',
            'active_ids': [picking_id],
            'active_id': picking_id,
        }
        wiz_transfer_obj = pool.get('stock.transfer_details')
        wiz_transfer_item_obj = pool.get('stock.transfer_details_items')
        wiz_transfer_id = wiz_transfer_obj.create(cr, 1, {'picking_id': picking_id}, context=context)
        wiz_transfer = wiz_transfer_obj.browse(cr, 1, wiz_transfer_id)

        # reset quantities received to zero for transfer lines which are not part of the incoming picking lines in the XML file
        # The goal is to retain only the transfer lines that were described in the incoming XML. The quantities are already correct;
        # the previous for-loop took care of that.
        # Note: the transfer wizard will only contain available lines, so if the order contained multiple lines for the same
        # product, and some are not available, they won't show up here. So no need for complex logic.
        transfer_lines_to_reset = [item.id for item in wiz_transfer.item_ids if item.product_id.x_new_ref not in [x.get('name') for x in picking_lines]]
        wiz_transfer_item_obj.write(cr, 1, transfer_lines_to_reset, {'quantity': 0})

        wiz_transfer_obj.do_detailed_transfer(cr, 1, [wiz_transfer_id])
