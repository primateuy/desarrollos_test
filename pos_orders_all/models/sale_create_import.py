# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date, datetime
from odoo.fields import Command


class SaleOrder(models.Model):
	_inherit = 'sale.order'


	@api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed', 'currency_id')
	def _compute_tax_totals(self):
		for order in self:
			order_lines = order.order_line.filtered(lambda x: not x.display_type)
			order.tax_totals = self.env['account.tax']._prepare_tax_totals(
				[x._convert_to_tax_base_line_dict() for x in order_lines],
				order.currency_id or order.company_id.currency_id,
			)
			total = 0
			for line in order.order_line:
				total +=line.price_subtotal


			order.tax_totals.update({
				'amount_untaxed':total,
			})

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	discount_type = fields.Selection([('percentage', "Percentage"), 
		('fixed', "Fixed")], string='Discount Type', default='percentage',readonly=True)


	def _prepare_invoice_line(self, **optional_values):
		"""Prepare the values to create the new invoice line for a sales order line.

		:param optional_values: any parameter that should be added to the returned invoice line
		:rtype: dict
		"""
		self.ensure_one()
	  
		res = {
			'display_type': self.display_type or 'product',
			'discount_line_type':self.discount_type,
			'sequence': self.sequence,
			'name': self.name,
			'product_id': self.product_id.id,
			'product_uom_id': self.product_uom.id,
			'quantity': self.qty_to_invoice,
			'discount': self.discount,
			'price_unit': self.price_unit,
			'tax_ids': [Command.set(self.tax_id.ids)],
			'sale_line_ids': [Command.link(self.id)],
			'is_downpayment': self.is_downpayment,
		}
		self._set_analytic_distribution(res, **optional_values)
		if optional_values:
			res.update(optional_values)
		if self.display_type:
			res['account_id'] = False
		return res


	# @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
	# def _compute_amount(self):
	# 	res = super(SaleOrderLine, self)._compute_amount()
	# 	for line in self:
	# 		if line.discount_type == 'fixed':
	# 			if line.price_unit == 0:
	# 				price = 0 
	# 			else:
	# 				price = (line.price_unit*line.product_uom_qty) - line.discount
	# 			taxes = line.tax_id.compute_all(price, line.order_id.currency_id, 1, product=line.product_id, partner=line.order_id.partner_shipping_id)
				
	# 		else:
	# 			price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

	# 			taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)

	# 		line.update({
	# 			'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
	# 			'price_total': taxes['total_included'],
	# 			'price_subtotal': taxes['total_excluded'],
	# 		}) 
	# 	return res

	def _convert_to_tax_base_line_dict(self, **kwargs):

		self.ensure_one()
		base_tax_line = super(SaleOrderLine, self)._convert_to_tax_base_line_dict(**kwargs)
		if self.discount_type == 'fixed':
			if self.price_unit == 0:
				price = 0 
			else:
				price = (self.price_unit*self.product_uom_qty) - self.discount
		else:
			price = self.price_unit 

		base_tax_line['price_unit'] = price
		return base_tax_line
			
			


class InheritPOSOrder(models.Model):
	_inherit = 'pos.order'

	sale_order_ids = fields.Many2many('sale.order',string="Imported Sale Order(s)")

	def _order_fields(self, ui_order):
		res = super(InheritPOSOrder, self)._order_fields(ui_order)
		config = self.env['pos.session'].browse(ui_order['pos_session_id']).config_id
		# import sale functionality
		
		if 'imported_sales' in ui_order and ui_order.get('imported_sales'):
			so = ui_order['imported_sales'].split(',')
			so.pop()
			so_ids = []
			sale_orders = []
			for odr in so:
				sale = self.env['sale.order'].browse(int(odr))
				if sale :
					so_ids.append(sale.id)
					sale_orders.append(sale)
			res.update({
				'sale_order_ids': [(6,0,so_ids)]
			})

			if config.cancle_order:
				for s in sale_orders:
					s._action_cancel()
				
		return res

	def create_sales_order(self, partner_id, orderlines,cashier_id):
		sale_object = self.env['sale.order']
		sale_order_line_obj = self.env['sale.order.line']
		order_id = sale_object.create({'partner_id': partner_id, 'user_id': cashier_id})
		for dict_line in orderlines:
			product_obj = self.env['product.product']
			product_dict = dict_line.get('product')

			product_tax = product_obj.browse(product_dict.get('id'))
			tax_ids = []
			for tax in product_tax.taxes_id:
				tax_ids.append(tax.id)

			product_name = product_obj.browse(product_dict.get('id')).name
			if product_dict.get('discount_method') == 'fixed' and product_dict.get('discount') != 0:	
				order_line_search = sale_order_line_obj.sudo().search([('name','=','Fixed Discount'),('order_id','=',order_id.id)])
				if not order_line_search:
					sale_order_line_obj.create({
							'display_type': 'line_note',
							'name': 'Fixed Discount',
							'order_id': order_id.id,
						})	
			vals = {'product_id': product_dict.get('id'),
					'name': product_name,
					'product_uom_qty': product_dict.get('quantity'),
					'price_unit': product_dict.get('price'),
					'product_uom': product_dict.get('uom_id'),
					'tax_id': [(6, 0, tax_ids)],
					'discount': product_dict.get('discount'),
					'discount_type': product_dict.get('discount_method'),
					'order_id': order_id.id}
			sale_order_line_obj.create(vals)
						
				# return order_id.name