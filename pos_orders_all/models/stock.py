# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
import random
from odoo.tools import float_is_zero
from datetime import date, datetime
from odoo.exceptions import UserError, ValidationError
import json


class stock_quant(models.Model):
	_inherit = 'stock.move'

	@api.model
	def sync_product(self, prd_id):
		notifications = []
		pos_configs = self.env['pos.config'].sudo().search([('display_stock','=',True)])
		if pos_configs:
			ssn_obj = self.env['pos.session'].sudo()
			prod_fields = ssn_obj._loader_params_product_product()['search_params']['fields']
			# prod_fields.pop(prod_fields.index('taxes_id'))
			prod_obj = self.env['product.product'].sudo()

			product = prod_obj.with_context(display_default_code=False).search_read([('id', '=', prd_id)],prod_fields)
			product_id = prod_obj.search([('id', '=', prd_id)]) 

			res = product_id._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))
			product[0]['qty_available'] = res[product_id.id]['qty_available']
			if product :
				categories = ssn_obj._get_pos_ui_product_category(ssn_obj._loader_params_product_category())
				product_category_by_id = {category['id']: category for category in categories}
				product[0]['categ'] = product_category_by_id[product[0]['categ_id'][0]]
				vals = {
					'id': [product[0].get('id')], 
					'product': product,
					'access':'pos.sync.product',
				}
				notifications.append([self.env.user.partner_id,'product.product/sync_data',vals])
			if len(notifications) > 0:
				self.env['bus.bus']._sendmany(notifications)
		return True


	@api.model_create_multi
	def create(self, vals_list):
		res = super(stock_quant, self).create(vals_list)

		notifications = []
		for rec in res:
			rec.sync_product(rec.product_id.id)
		return res

	def write(self, vals):
		res = super(stock_quant, self).write(vals)
		notifications = []
		for rec in self:
			rec.sync_product(rec.product_id.id)
		return res



class product(models.Model):
	_inherit = 'product.product'
	
	quant_text = fields.Text('Quant Qty', compute='_compute_avail_locations', store=True)


	def get_low_stock_products(self,low_stock):
		products=self.search([('detailed_type', '=' ,'product')]);
		product_list=[]
		for product in products:
			if product.qty_available <= low_stock:
				product_list.append(product.id)
		return product_list
	@api.depends('stock_quant_ids', 'stock_quant_ids.product_id', 'stock_quant_ids.location_id',
				 'stock_quant_ids.quantity')
	def _compute_avail_locations(self):
		notifications = []
		for rec in self:
			final_data = {}
			rec.quant_text = json.dumps(final_data)
			if rec.type == 'product':
				quants = self.env['stock.quant'].sudo().search(
					[('product_id', 'in', rec.ids), ('location_id.usage', '=', 'internal')])
				for quant in quants:
					loc = quant.location_id.id
					if loc in final_data:
						last_qty = final_data[loc][0]
						final_data[loc][0] = last_qty + quant.quantity
					else:
						final_data[loc] = [quant.quantity, 0, 0]
				rec.quant_text = json.dumps(final_data)
		return True
	

class StockPicking(models.Model):
	_inherit='stock.picking'

	@api.model
	def _create_picking_from_pos_order_lines(self, location_dest_id, lines, picking_type, partner=False):
		"""We'll create some picking based on order_lines"""

		pickings = self.env['stock.picking']
		stockable_lines = lines.filtered(
			lambda l: l.product_id.type in ['product', 'consu'] and not float_is_zero(l.qty,
																					  precision_rounding=l.product_id.uom_id.rounding))
		if not stockable_lines:
			return pickings
		positive_lines = stockable_lines.filtered(lambda l: l.qty > 0)
		negative_lines = stockable_lines - positive_lines

		if positive_lines:
			pos_order = positive_lines[0].order_id
			location_id = pos_order.location_id.id
			vals = self._prepare_picking_vals(partner, picking_type, location_id, location_dest_id)
			positive_picking = self.env['stock.picking'].create(vals)
			positive_picking._create_move_from_pos_order_lines(positive_lines)
			try:
				with self.env.cr.savepoint():
					positive_picking._action_done()
			except (UserError, ValidationError):
				pass

			pickings |= positive_picking
		if negative_lines:
			if picking_type.return_picking_type_id:
				return_picking_type = picking_type.return_picking_type_id
				return_location_id = return_picking_type.default_location_dest_id.id
			else:
				return_picking_type = picking_type
				return_location_id = picking_type.default_location_src_id.id

			vals = self._prepare_picking_vals(partner, return_picking_type, location_dest_id, return_location_id)
			negative_picking = self.env['stock.picking'].create(vals)
			negative_picking._create_move_from_pos_order_lines(negative_lines)
			try:
				with self.env.cr.savepoint():
					negative_picking._action_done()
			except (UserError, ValidationError):
				pass
			pickings |= negative_picking
		return pickings