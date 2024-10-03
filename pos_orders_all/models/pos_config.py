# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date, datetime


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	# pos orders screen
	show_order = fields.Boolean('Show Orders',related="pos_config_id.show_order",readonly=False,)
	pos_pos_session_limit = fields.Selection(related="pos_config_id.pos_session_limit", readonly=False, string='Session limit',)
	show_barcode = fields.Boolean('Show Barcode in Receipt',related="pos_config_id.show_barcode",readonly=False)
	show_draft = fields.Boolean('Show Draft Orders',related="pos_config_id.show_draft",readonly=False)
	show_posted = fields.Boolean('Show Posted Orders',related="pos_config_id.show_posted",readonly=False)

	# import sale functionality
	pos_check = fields.Boolean(related='pos_config_id.check', readonly=False)
	pos_load_orders_days = fields.Integer(related='pos_config_id.load_orders_days', readonly=False)
	pos_load_draft_sent = fields.Boolean(related='pos_config_id.load_draft_sent', readonly=False)
	pos_cancle_order = fields.Boolean(related='pos_config_id.cancle_order', readonly=False)

	credit_note = fields.Selection(related="pos_config_id.credit_note", readonly=False, string = "Credit note configuration")

	#Invoice auto check
	auto_check_invoice = fields.Boolean(related='pos_config_id.auto_check_invoice', readonly=False ,string='Invoice Auto Check')

	#pos stock
	pos_display_stock = fields.Boolean(related="pos_config_id.display_stock",readonly=False)
	pos_pos_stock_type = fields.Selection(related="pos_config_id.pos_stock_type", readonly=False,string='Stock Type', help='Seller can display Different stock type in POS.')
	pos_pos_allow_order = fields.Boolean(string='Allow POS Order When Product is Out of Stock',readonly=False,related="pos_config_id.pos_allow_order")
	pos_pos_deny_order = fields.Char(string='Deny POS Order When Product Qty is goes down to',readonly=False,related="pos_config_id.pos_deny_order")

	show_stock_location = fields.Selection(string='Show Stock Of',readonly=False, related="pos_config_id.show_stock_location")

	stock_location_id = fields.Many2one(
		'stock.location', string='Stock Location',
		domain=[('usage', '=', 'internal')], related="pos_config_id.stock_location_id",readonly=False)
	stock_position = fields.Selection(related="pos_config_id.stock_position", readonly=False,string='Stock Position',required=True)
	color_background = fields.Char(string='Background Color',readonly=False,related="pos_config_id.color_background")
	font_background = fields.Char(string='Font Color',readonly=False,related="pos_config_id.font_background")
	low_stock = fields.Float(string='Product Low Stock',readonly=False,related="pos_config_id.low_stock")


	# bag charges functionality
	pos_pos_bag_category_id = fields.Many2one('pos.category',related='pos_config_id.pos_bag_category_id',readonly=False,string='Bag Charges Category')
	allow_bag_charges = fields.Boolean(related="pos_config_id.allow_bag_charges", readonly=False, string='Allow Bag Charges')

	#discount
	discount_type = fields.Selection(related='pos_config_id.discount_type',readonly=False)





class pos_config(models.Model):
	_inherit = 'pos.config'
	
	# pos orders screen
	show_order = fields.Boolean('Show Orders')
	pos_session_limit = fields.Selection([('all',  "Load all Session's Orders"), ('last3', "Load last 3 Session's Orders"), ('last5', " Load last 5 Session's Orders"),('current_day', "Only Current Day Orders"), ('current_session', "Only Current Session's Orders")], string='Session limit',default="current_day")
	show_barcode = fields.Boolean('Show Barcode in Receipt')
	show_draft = fields.Boolean('Show Draft Orders')
	show_posted = fields.Boolean('Show Posted Orders')

	# import sale functionality
	check = fields.Boolean(string='Import Sale Order', default=False)
	load_orders_days = fields.Integer('Load Orders of Last Days')
	load_draft_sent = fields.Boolean(string='Load only draft/sent sale orders', default=False)
	cancle_order = fields.Boolean(string='Cancel Sale Order after Import', default=False)

	# bag charges functionality
	pos_bag_category_id = fields.Many2one('pos.category', 'Bag Charges Category')
	allow_bag_charges = fields.Boolean('Allow Bag Charges')

	auto_check_invoice = fields.Boolean(string='Invoice Auto Check') 

	# discount
	discount_type = fields.Selection([('percentage', "Percentage"), 
		('fixed', "Fixed")], string='Discount Type', default='percentage', 
		help='Seller can apply different Discount Type in POS.')


	# pos stock
	def _get_default_location(self):
		
		location = self.env['stock.warehouse'].search(self.env['stock.warehouse']._check_company_domain(self.env.company), limit=1).lot_stock_id
		return location

	display_stock = fields.Boolean(string='Display Stock in POS')
	pos_stock_type = fields.Selection(
		[('onhand', 'Qty on Hand'),('available', 'Qty Available')], default='onhand', string='Stock Type', help='Seller can display Different stock type in POS.')
	pos_allow_order = fields.Boolean(string='Allow POS Order When Product is Out of Stock')
	pos_deny_order = fields.Char(string='Deny POS Order When Product Qty is goes down to')
	stock_position = fields.Selection(
		[('top_right', 'Top Right'), ('top_left', 'Top Left'), ('bottom_right', 'Bottom Right')], default='top_left', string='Stock Position')

	show_stock_location = fields.Selection([
		('all', 'All Warehouse'),
		('specific', 'Current Session Warehouse'),
	], string='Show Stock Of', default='all')

	stock_location_id = fields.Many2one(
		'stock.location', string='Stock Location',
		domain=[('usage', '=', 'internal')], required=True, default=_get_default_location)
	
	color_background = fields.Char(
		string='Color',)
	font_background = fields.Char(
		string='Font Color',)
	low_stock = fields.Float(
		string='Product Low Stock',default=0.00)

	# Credit note
	credit_note = fields.Selection([('create_note','Create Return order Credit note'),
		('not_create_note','Do not Create Return order Credit note')], string = "Credit note configuration" , default = "create_note")
