from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.tools.translate import _
from openerp.addons.website_sale.controllers.main import website_sale

from openerp.addons.ip_web_addons import jsend, tools

class Ecommerce(website_sale):

    NO_ORDER = 'No Order'

    @jsend.jsend_error_catcher
    @http.route(['/shop/add_cart_multi/'], type='http', auth="public", methods=['POST'], website=True, multilang=True)
    def add_cart_multi(self, **product_quantity_map):
        """
        Add multiple products to the cart with specified quantities
        @param dict product_quantity_map: A dictionary keyed by product IDs where values represent quantities
        """
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        fail_check = jsend.FailCheck()

        if not hasattr(product_quantity_map, '__iter__'):
            fail_check.add('product_quantity_map', 'product_quantity_map should be a json object mapping product IDs to quantities to add to the cart')

        for product_id, quantity in product_quantity_map.items():
            # data validation
            if not tools.isnumeric(product_id):
                fail_check.add('product_id', 'Product IDS must be numeric')
            if not tools.isnumeric(quantity):
                fail_check.add('quantity', 'Quantity must be numeric')

            if fail_check.failed():
                return fail_check.fail()

            product_id = int(product_id)
            quantity = float(quantity)


            new_quantity = self.cart_update(
                product_id,
                add_qty=quantity
                )
            # bug in _ecommerce_add_product_to_cart means that if adding a new product to the cart,
            # the quantity is always set to 1. Handle this by checking returned qty against specified
            # quantity and adjust it accordingly

            print new_quantity

            '''if new_quantity < quantity:
                self.cart_update(product_id,
                add_qty=quantity - new_quantity
                )'''
        return self.get_cart_info()

    @jsend.jsend_error_catcher
    @http.route(['/shop/get_cart_info/'], type='http', auth="public", website=True, multilang=True)
    def get_cart_info(self):
        """
        Get the IDS and quantities of products in the cart
        """
        order = request.website.sale_get_order()
        
        if not order:
            return jsend.jsend_fail({'order': 'There are no current orders for this customer'})

        if order.cart_quantity ==0:
            order.draft_auto_ship = False
        
        contains_autoship = order.draft_auto_ship
        
        product_quantites = dict([(line.product_id.id, line.product_uom_qty) for line in order.order_line])
        for line in order.order_line:
            product_quantites[line.product_id.id] += line.product_uos_qty
            
      

        vals = {
            'contains_autoship' : contains_autoship,
            'product_quantities': product_quantites,
            'total_price': order.amount_total,
            'product_count': order.cart_quantity
        }
        return jsend.jsend_success(vals)
