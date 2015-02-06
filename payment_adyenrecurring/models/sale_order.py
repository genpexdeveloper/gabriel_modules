from openerp.osv import osv, fields
from openerp.tools.translate import _

class sale_order(osv.osv):

	_inherit = "sale.order"

	_columns = {
		'shopperReference': fields.char('shopperReference', help="shopperReference used to identify shopper with ADYEN"),
	}

	def create_auto_ship(self, cr, uid, so_id, interval=0, end_date=None, context=None):
		auto_ship_id = super(sale_order, self).create_auto_ship(cr, uid, so_id, interval, end_date, context=context)

		#Copy shopperReference in autoship
		auto_ship_obj = self.pool['ip_web_addons.auto_ship']
		so = self.browse(cr, uid, so_id)

		auto_ship_obj.write(cr, uid, auto_ship_id, {'shopperReference': so.shopperReference}, context=context)

		return auto_ship_id

	def _request_adyenrecurring_payment(self, cr, uid, order_id, context=None):
		sord = self.pool['sale.order'].browse(cr, uid, order_id, context)
		if sord.auto_ship_id:
			payment = self.pool['ip_web_addons.auto_ship'].request_payment(cr, uid, sord.auto_ship_id.id, sord.amount_total, sord.currency_id.name, sord.partner_id.email, sord.name, sord, context=context)
		return False
	
	def action_wait(self, cr, uid, ids, context=None):
		super(sale_order, self).action_wait(cr, uid, ids, context=context)
		for o in self.browse(cr, uid, ids):
			if o.order_line and o.auto_ship_id:
				self._request_adyenrecurring_payment(cr, uid, o.id, context=context)
