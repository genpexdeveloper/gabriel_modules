# -*- coding: utf-8 -*-
from openerp.osv import osv, fields

class Size(osv.osv):
	""" Defines reusable product sizes for IP products, i.e. small, large etc """

	_name = "ip_web.size"

	_columns = {
		"name": fields.char("Name", size=64),
	}
