# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime
import time
from openerp.osv import osv
from openerp.tools.translate import _

from ads_data import ads_data
from tools import convert_date

class ads_sales_order(ads_data):
    """
    Handles the importation and exportation of a sales order's delivery order
    """

    file_name_prefix = ['CMDE', 'CREX']
    xml_root = 'orders'

    def extract(self, picking_out):
        """
        Takes a stock.picking browse_record and extracts the
        appropriate data into self.data

        @param picking_out: browse_record(stock.picking)
        """
        picking = picking_out.pool['stock.picking'].browse(picking_out._cr, 1, picking_out.id)
        shipping_partner = picking_out.sale_id.partner_shipping_id
        invoice_partner = picking_out.sale_id.partner_invoice_id
        carrier_name = picking_out.sale_id.carrier_id and picking_out.sale_id.carrier_id.ads_ref or ''

        # Delivery method can also be added as a move line, so find all move lines whose products
        # are the delivery products of a delivery method and save IDS and ads ref for later
        carrier_move_ids = []
        if not carrier_name:
            carrier_obj = picking_out.pool['delivery.carrier']
            product_obj = picking_out.pool['product.product']

            product_ids = [move.product_id.id for move in picking_out.move_lines if move.product_id]
            carrier_map = product_obj.is_delivery_method(picking_out._cr, 1, product_ids)

            carrier_product_ids = [k for k, v in carrier_map.iteritems() if v]
            carrier_move_ids = [move.id for move in picking.move_lines if move.product_id and move.product_id.id in carrier_product_ids]

            for move in picking_out.move_lines:
                if move.id in carrier_move_ids:
                    carrier = carrier_obj.browse(picking_out._cr, 1, carrier_map[move.product_id.id][0])
                    carrier_name = carrier.ads_ref or ''

        so_data = {
            # general
            'NUM_CMDE': picking.ads_send_number and picking_out.sale_id.name + '-' + str(picking.ads_send_number) or picking_out.sale_id.name,
            'NUM_FACTURE_BL': picking_out.name,
            'DATE_EDITION': convert_date(picking_out.date),
            'MONTANT_TOTAL_TTC': picking_out.sale_id.amount_total,
            'DATE_ECHEANCE': convert_date(picking_out.min_date),
            'TYPE_ENVOI': carrier_name,

            # invoice_partner address and contact
            'SOCIETE_FAC': invoice_partner.is_company and invoice_partner.name or '',
            'NOM_CLIENT_FAC': invoice_partner.name or '',
            'ADR1_FAC': invoice_partner.street or '',
            'ADR2_FAC': invoice_partner.street2 or '',
            'CP_FAC': invoice_partner.zip or '',
            'VILLE_FAC': invoice_partner.city or '',
            'ETAT_FAC': invoice_partner.state_id and invoice_partner.state_id.name or '',
            'PAYS_FAC': invoice_partner.country_id and invoice_partner.country_id.name or '',
            'CODE_ISO_FAC': invoice_partner.country_id and invoice_partner.country_id.code or '',

            # delivery address and contact
            'SOCIETE_LIV': shipping_partner.is_company and shipping_partner.name or '',
            'NOM_CLIENT_LIV': shipping_partner.name or '',
            'ADR1_LIV': shipping_partner.street or '',
            'ADR2_LIV': shipping_partner.street2 or '',
            'CP_LIV': shipping_partner.zip or '',
            'VILLE_LIV': shipping_partner.city or '',
            'ETAT_LIV': shipping_partner.state_id and shipping_partner.state_id.name or '',
            'PAYS_LIV': shipping_partner.country_id and shipping_partner.country_id.name or '',
            'CODE_ISO_LIV': shipping_partner.country_id and shipping_partner.country_id.code or '',
            'TELEPHONE_LIV': shipping_partner.phone or u'no_phone',
            'EMAIL_LIV': shipping_partner.email or u'noemail@incontinence-protection.com',
        }

        # asserts for required data
        required_data = {
            'NUM_CMDE': 'The picking was not created by a sales order',
            'NUM_FACTURE_BL': 'This should never happen - please contact OpenERP',
            'NOM_CLIENT_FAC': 'Invoice partner name',
            'ADR1_FAC': 'Invoice partner address line 1',
            'CP_FAC': 'Invoice partner zip',
            'VILLE_FAC': 'Invoice partner city',
            'CODE_ISO_FAC': 'Invoice partner country',
            'NOM_CLIENT_LIV': 'Shipping partner name',
            'ADR1_LIV': 'Shipping partner address line 1',
            'CP_LIV': 'Shipping partner zip',
            'VILLE_LIV': 'Shipping partner city',
            'CODE_ISO_LIV': 'Shipping partner country',
            'TELEPHONE_LIV': 'Shipping partner phone',
            'MONTANT_TOTAL_TTC': 'This should never happen - please contact OpenERP',
        }

        missing_data = {}
        for field in required_data:
            if not so_data[field]:
                missing_data[field] = required_data[field]

        if missing_data:
            message = _('While processing sales order %s and picking_out %s there was some data missing for the following required fields:' \
                        % (so_data['NUM_CMDE'], so_data['NUM_FACTURE_BL'])) + '\n\n' \
                      + "\n".join(sorted(['- ' + _(missing_data[data]) for data in missing_data]))\
                      + '\n\n' + _('These fields must be filled before we can continue')
            raise osv.except_osv(_('Missing Required Data'), message)

        self.insert_data('order', so_data)

        line_seq = 1
        for move in picking_out.move_lines:

            # skip lines that are cancelled, or don't have a product, or have a discount, delivery method or service product
            if move.state == 'cancel' \
            or not move.product_id \
            or move.id in carrier_move_ids \
            or move.product_id.discount \
            or move.product_id.type == 'service':
                continue

            # Raise error if missing x_new_ref
            if not move.product_id.x_new_ref:
                raise osv.except_osv(_('Missing Reference'), _('Product "%s" on picking_out "%s" is missing an IP Reference. One must be entered before we can continue.') % (move.product_id.name, picking_out.name) )

            line = {
                'NUM_FACTURE_BL': picking_out.name,
                'CODE_ART': move.product_id.x_new_ref,
                'LIBELLE_ART': move.product_id.name or '',
                'QTE': move.product_qty,
                'OBLIGATOIRE': '1',
            }
            self.insert_data('order.articles.line', line)
            line_seq += 1

        return self

    def upload(self, cr, ads_manager):
        """
        Only upload BL's with article lines. Otherwise, all articles are non-uploadable (service,
        discount, delivery product), so return False  so the BL can be automatically closed at sale_order.py level.

        Save uploaded file name to ads_file_name field.
        """
        if self.data['order']['articles']:
            res = super(ads_sales_order, self).upload(cr, ads_manager)
            if self.browse_record and self.file_name:
                self.browse_record.write({'ads_file_name': self.file_name})
            return res
        else:
            return False

    def _find_picking(self, cr, picking_out_obj, picking_name):
        """ Finds pickings by name. If name >= 30, use wildcard at end due to length limitations of ADS """
        if len(picking_name) < 30:
            return picking_out_obj.search(cr, 1, [('name', '=', picking_name)])
        else:
            return picking_out_obj.search(cr, 1, [('name', 'ilike', picking_name)])

    def process(self, pool, cr, expedition):
        """
        Update picking tracking numbers / cancel picking orders
        @param pool: OpenERP object pool
        @param cr: OpenERP database cursor
        @param AutoVivification expedition: Data from ADS describing the expedition of the SO
        """
        # extract information
        assert 'NUM_FACTURE_BL' in expedition, 'An expedition has been skipped because it was missing a NUM_FACTURE_BL'

        picking_name = expedition['NUM_FACTURE_BL']
        status = 'STATUT' in expedition and expedition['STATUT'] or ''
        tracking_number = 'NUM_TRACKING' in expedition and expedition['NUM_TRACKING'] or ''

        # find original picking
        picking_out_obj = pool.get('stock.picking')
        picking_ids = self._find_picking(cr, picking_out_obj, picking_name)

        assert len(picking_ids) == 1, 'Found %s pickings with name %s. Should have found 1' % (len(picking_ids), picking_name)
        picking_id, = picking_ids
        picking_out = picking_out_obj.browse(cr, 1, picking_id)

        # set / append tracking number on picking
        if tracking_number:
            try:
                if picking_out.carrier_tracking_ref:
                    existing_tracking_number = picking_out.carrier_tracking_ref.split(',')
                    if str(tracking_number) not in existing_tracking_number:
                        existing_tracking_number.append(tracking_number)
                    tracking_number = ','.join(map(str, existing_tracking_number))
            except:
                pass
            picking_out_obj.write(cr, 1, picking_id, {'carrier_tracking_ref': tracking_number})

        # if status is R, order has been cancelled by ADS because of lack of stock. We then need to
        # upload the same BL with a new name and new SO name. We handle this by cancelling BL,
        # duplicating it, confirming it then fixing the SO state from shipping_except
        if status == 'R':

            assert picking_out.state in ['assigned', 'confirmed'], \
                _("The picking %s was not in state assigned or confirmed, and therefore cannot be cancelled") % picking_name

            picking_obj = pool['stock.picking']
            picking_out_obj = pool['stock.picking']
            sale_order_obj = pool['sale.order']

            # get stock.picking version of stock.picking for access to send number field
            picking = picking_obj.browse(cr, 1, picking_out.id)
            sale = picking.sale_id

            # value for new picking's ads_send_number
            send_number = picking.ads_send_number + 1 or 1

            # Cancel original picking, then duplicate and confirm it
            picking_out_obj.action_cancel(cr, 1, [picking_id])

            # specify a name for the new BL otherwise stock module will delete the origin from it's values
            defaults = {
                'ads_send_number': send_number,
                'name': pool['ir.sequence'].get(cr, 1, 'stock.picking')
            }

            picking_id = picking_obj.copy(cr, 1, picking_id, defaults)
            picking_obj.signal_button_confirm(cr, 1, [picking_id])

            # fix sale order state from shipping_except to in progress
            sale_values = {}
            if sale.state == 'shipping_except':
                sale_values['state'] = 'progress'
                sale_values['shipped'] = False

                if (sale.order_policy == 'manual'):
                    for line in sale.order_line:
                        if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                            sale_values['state'] = 'manual'
                            break
            if sale_values:
                sale_order_obj.write(cr, 1, sale.id, sale_values)
        return True
