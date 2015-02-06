# -*- coding: utf-8 -*-
from openerp.osv import osv, fields

class Product(osv.osv):

    _inherit = 'product.product'

    _columns = {
        'x_description': fields.text('Website Description'),
        'x_code_lpp': fields.char('Code LPP'),
        'x_image2': fields.binary('Image 2'),
        'x_image3': fields.binary('Image 3'),
        'x_image4': fields.binary('Image 4'),
        'x_image5': fields.binary('Image 5'),
        'x_new_ref': fields.char('IP Ref'),
        'x_pallet_quantity': fields.integer('Quantity in Pallet'),
        'x_substitute': fields.many2many('product.product', 'product_substitute_rel', 'product_id', 'substitute_id', 'Frequently Bought Together'),
        'x_waist': fields.char('Waist Measurement'),
        'x_other_purchases': fields.many2many('product.product', 'product_other_purchases_rel', 'product_id', 'other_purchase_id', 'People who bought this item also bought'),
        'x_absorption': fields.float('Absorption'),
        'x_bag_quantity': fields.integer('Bag Quantity'),
        'x_bag_dimension': fields.char('Bag Dimension'),
        'x_box_quantity': fields.integer('Box Quantity'),
    }
