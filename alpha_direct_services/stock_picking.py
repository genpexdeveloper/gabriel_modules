from ftplib import error_perm
# from copy import copy

from openerp.tools.translate import _
from openerp.osv import osv, fields

from ads_sales_order import ads_sales_order
from ads_purchase_order import ads_purchase_order



def upload_so_picking(stock_picking_obj, cr, uid, picking_id, context=None):
    """
    Extract and upload the picking to the server. If upload returns False, it means
    there were no deliverable BL lines and it should be automatically marked delivered.
    If there is an exception it will be raised.
    """
    picking = stock_picking_obj.browse(cr, uid, picking_id, context=context)
    data = ads_sales_order(picking)
    data.upload(cr, stock_picking_obj.pool.get('ads.manager'))

def upload_po_picking(stock_picking_obj, cr, uid, picking_id, vals={}, context=None):
    """
    Extract and upload the picking to the server.
    If there is an exception it will be raised.
    """
    picking = stock_picking_obj.browse(cr, uid, picking_id, context=context)
    data = ads_purchase_order(picking)
    data.upload(cr, stock_picking_obj.pool.get('ads.manager'))

def all_assigned(picking_obj, cr, ids):
    """ Returns true if all pickings have state 'assigned' """
    for picking in picking_obj.read(cr, 1, ids, ['state']):
        if picking['state'] != 'assigned':
            return False
    return True

def pick_cancel_manuel(obj, cr, uid, ids, context=None):
    """
    Called when manually cancelling a picking.
    If picking was uploaded and file still exists on the server, delete it and cancel the picking.
    If it no longer exists on the server, raise an error.
    If picking was never uploaded, just cancel the picking.
    """

    def cannot_cancel():
        """ Raise OE exception saying picking was already imported and cannot be canceled """
        raise osv.except_osv(_("Cannot Cancel Delivery Order"), _("The delivery order has already been imported by ADS so it cannot be canceled anymore"))

    for picking in obj.browse(cr, uid, ids):
        picking_id = picking.id

        # Was it uploaded?
        if picking.ads_file_name:
            with obj.pool['ads.manager'].connection(cr) as conn:
                try:
                    # Try to delete the file from the server
                    conn.delete_data(picking.ads_file_name)

                    # Reset the sent flah and file name, then cancel
                    obj.write(cr, uid, picking_id, {'ads_sent': False, 'ads_file_name': False})
                    obj.action_cancel(cr, uid, [picking_id], context=context)
                except error_perm, e:
                    # Cannot delete the file so it's already been imported to ADS. Raise an error
                    cannot_cancel()
        else:
            # Never uploaded to cancel picking
            obj.action_cancel(cr, uid, [picking_id], context=context)
    return True

class stock_picking(osv.osv):
    """
    Inherit the stock.picking to prevent manual processing.

    If ADS does not have stock to fulfill an order, they cancel the order and we have to re-upload
    it with a different BL and SO number. To handle this we cancel the BL, duplicate it (incrementing
    the name automatically) then append the value of the ads_send_number field to the end of the original
    SO name.
    """

    _inherit = 'stock.picking'
    _columns = {
        'ads_sent': fields.boolean('Sent to ADS?'),
        'ads_send_number': fields.integer('Send Number', help="Number of times this picking has been sent to ADS - used to re-send cancelled orders"),
        'ads_file_name': fields.char('Sent to ADS?', size=40, help="The name of the file uploaded to ADS"),
    }

    def action_process(self, cr, uid, ids, context=None):
        if all_assigned(self, cr, ids):
            raise osv.except_osv(_('Cannot Process Manually'), _("The picking should be processed in the ADS system. It will then be automatically synchronized to OpenERP."))
        else:
            super(stock_picking, self).action_process(cr, uid, ids, context=context)

    def cancel_manuel(self, cr, uid, ids, context=None):
        """ Manual cancellation by user on form view """
        return pick_cancel_manuel(self, cr, uid, ids, context=context)

    def action_disallow_invoicing(self, cr, uid, ids, context=None):
        """ When picking is received automatically it is set as invoicable. Add option to make non invoicable """
        self.write(cr, uid, ids, {'invoice_state': 'none'})

    def ads_manuel_upload(self, cr, uid, ids, context=None):
        """
        Upload this picking to ADS. If a file_name already exists on the picking, try to delete
        it from the server, then upload again and set new file_name.
        """
        for picking_id in ids:
            picking = self.browse(cr, uid, picking_id, context=context)

            # make sure state is correct
            if not picking.state == 'assigned':
                continue

            # try to delete existing file
            if picking.ads_file_name:
                with self.pool['ads.manager'].connection(cr) as conn:
                    try:
                        conn.delete_data(picking.ads_file_name)
                    except error_perm, e:
                        pass

            # upload file
            if picking.picking_type_id.code == 'incoming':
                data = ads_purchase_order(picking)
            elif picking.picking_type_id.code == 'outgoing':
                data = ads_sales_order(picking)
            else:
                raise osv.except_osv(_("Incorrect picking type"), _("There was an error: this stock picking is neither incoming nor outgoing, so I don't know what to send to ADS."))
            data.upload(cr, self.pool.get('ads.manager'))
        return True

    def is_return(self, pick):
        """ Seems to be the only way to check if an IN is a return or not ... """
        return ('-' in pick.name and sorted(pick.name.split('-'), reverse=True)[0].startswith('ret'))

    def copy(self, cr, uid, id, default=None, context=None):
        """ Set ads_sent back to False - caused by duplication during action_process of partial wizard """
        res = super(stock_picking, self).copy(cr, uid, id, default=default, context=context)
        self.write(cr, uid, res, {'ads_sent': False, 'ads_file_name': ''})
        return res

    def upload_to_ads(self, cr, uid, ids, context=None):
        """ Upload picking to ADS """

        if not hasattr(ids, '__iter__'):
            ids = [ids]

        for picking_id in ids:
            picking = self.browse(cr, uid, picking_id, context=context)
            if picking.ads_sent:
                continue
            picking_to_upload = False

            if picking.picking_type_code == 'outgoing' and not picking.ads_sent:

                # find other delivery orders for this SO in assigned state
                # partial_ids = self.search(cr, 1, [('sale_id','=',picking.sale_id.id),
                #                                 ('picking_type_id.code','=','outgoing'),
                #                                 ('state','in',['assigned','confirmed'])])
                # TODO: is this equivalent to the code above?
                partial_ids = set([picking.id])
                all_pickings_for_so = set([picking.id])
                if picking.group_id:
                    pickings_in_group_ids = self.search(cr, uid, [('group_id','=',picking.group_id.id)], context=context)
                    pickings_in_group = self.browse(cr, uid, pickings_in_group_ids, context=context)
                    for p in pickings_in_group:
                        all_pickings_for_so.add(p.id)
                        if p.picking_type_id.code == 'outgoing' and p.state in ['assigned', 'confirmed', 'partially_available']:
                            partial_ids.add(p.id)

                # Picking is a return, so simply upload it regardless of partials
                if 'ret' in picking.name:
                    picking_to_upload = picking_id

                # It's a normal non-partial picking, so upload it
                elif len(partial_ids) == 1:
                    picking_to_upload = picking_id

                # It's a partial, so it's the other picking that we are interested in.
                # Set ads_sent to False and upload if state is assigned. Otherwise wait for scheduler
                else:
                    partial_id = sorted(partial_ids)[0]
                    self.write(cr, uid, partial_id, {'ads_sent': False})
                    picking = self.browse(cr, 1, partial_id)

                    if picking.state == 'assigned':
                        picking_to_upload = partial_id

                # Finally, upload the picking if applicable
                if picking_to_upload:
                    try:
                        send_number = sorted([p.ads_send_number for p in self.browse(cr, 1, all_pickings_for_so)], reverse=True)[0] + 1

                        self.write(cr, 1, picking_to_upload, {'ads_send_number': send_number})
                        upload_so_picking(self, cr, uid, picking_to_upload, context=context)
                        self.write(cr, 1, picking_to_upload, {'ads_sent': True})
                    except:
                        # TODO: maybe do something more intelligent?
                        pass

            elif picking.picking_type_code == 'incoming' and not self.is_return(picking) and not picking.ads_sent:

                # detect if this picking is a partial
                # if picking.move_lines and picking.move_lines[0].purchase_line_id:
                #     purchase_id = picking.move_lines[0].purchase_line_id.order_id.id
                # other_line_ids = self.pool.get('stock.move').search(cr, uid, [('purchase_line_id.order_id', '=', purchase_id), ('picking_id','!=',picking.id)])
                is_partial = False
                if picking.group_id:
                    pickings_in_group_ids = self.search(cr, uid, [('group_id','=',picking.group_id.id)], context=context)
                    is_partial = len(pickings_in_group_ids) > 1

                if not is_partial:
                    try:
                        upload_po_picking(self, cr, 1, picking_id, context=context)
                        self.write(cr, 1, picking_id, {'ads_sent': True})
                    except:
                        # TODO: maybe do something more intelligent?
                        pass

        return True

    def cron_upload_to_ads(self, cr, uid=1):
        ids = self.pool.get(self._name).search(cr, uid, [('ads_sent', '=', False), ('state','in',['assigned', 'partially_available'])])
        self.upload_to_ads(cr, uid, ids, context=None)
