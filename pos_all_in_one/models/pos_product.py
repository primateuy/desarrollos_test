# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class PosSession(models.Model):
	_inherit = 'pos.session'


	def _loader_params_product_product(self):
		result = super()._loader_params_product_product()
		result['search_params']['fields'].append('categ_store_fields')
		return result

	def _loader_params_product_template(self):
		result = super()._loader_params_product_template()
		result['search_params']['fields'].append('categ_store_fields')
		return result


class pos_config(models.Model):
	_inherit = 'pos.config'

	allow_pos_product_operations = fields.Boolean(string='Allow Product Operations')
	allow_edit_product  = fields.Boolean(string='Allow user to edit/create product from pos')


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	allow_pos_product_operations = fields.Boolean(related='pos_config_id.allow_pos_product_operations',readonly=False)
	allow_edit_product = fields.Boolean(related='pos_config_id.allow_edit_product',readonly=False)


class POSSession(models.Model):
	_inherit = 'pos.session'

	def _loader_params_product_product(self):
		res = super(POSSession, self)._loader_params_product_product()
		fields = res.get('search_params').get('fields')
		fields.extend(['type'])
		res['search_params']['fields'] = fields
		return res

	def _pos_data_process(self, loaded_data):
		super()._pos_data_process(loaded_data)
		loaded_data['pos_category'] = loaded_data['pos.category']
		loaded_data['product.category'] = loaded_data['product.category']

	def _pos_ui_models_to_load(self):
		result = super()._pos_ui_models_to_load()
		result += [
			'product.category',
		]
		return result
	def _loader_params_account_tax(self):
		result = super()._loader_params_account_tax()
		result['search_params']['fields'].append('type_tax_use')
		return result

class stock_quant(models.Model):
	_inherit = 'stock.quant'

	@api.model_create_multi
	def create(self, vals):
		res = super(stock_quant, self).create(vals)
		for rec in res:
			rec.product_id.sync_product(rec.product_id.id)
		return res

	def write(self, vals):
		res = super(stock_quant, self).write(vals)
		for i in self:
			i.product_id.sync_product(i.product_id.id)
		return res

class ProductTemplate(models.Model):
	_inherit = 'product.template'

	categ_store_fields = fields.Char()
	custom_pos_categ_ids = fields.Many2many(related='pos_categ_ids',string="Custom Pos Category") 
	bi_pos_reports_catrgory = fields.Many2one('pos.category',string="POS Category",compute='_compute_pos_reports_catrgory',
		inverse='_set_bi_pos_reports_catrgory',domain="[('id', 'in', custom_pos_categ_ids)]",)

	def write(self, vals):
		res = super(ProductTemplate, self).write(vals)
		for rec in self:
			for pv in rec.product_variant_ids :
				pv.sync_product(pv.id)
		return res


	def _set_bi_pos_reports_catrgory(self):
		self._set_product_variant_field('bi_pos_reports_catrgory')


	@api.depends('product_variant_ids.bi_pos_reports_catrgory')
	def _compute_pos_reports_catrgory(self):
		self._compute_template_field_from_variant_field('bi_pos_reports_catrgory')


	@api.onchange('pos_categ_ids')
	def _onchange_pos_categ_ids(self):
		if self.pos_categ_ids:

			self.bi_pos_reports_catrgory = False


class ProductProduct(models.Model):
	_inherit = 'product.product'

	categ_store_fields = fields.Char()
	custom_pos_categ_ids = fields.Many2many(related='pos_categ_ids',string="Custom Pos Category",domain="[('id', 'in', custom_pos_categ_ids)]") 
	bi_pos_reports_catrgory = fields.Many2one('pos.category',string="POS Category",domain="[('id', 'in', custom_pos_categ_ids)]")

	@api.onchange('pos_categ_ids')
	def _onchange_pos_categ_ids(self):
		if self.pos_categ_ids:
			
			self.bi_pos_reports_catrgory = False


	@api.model
	def sync_product(self, prd_id):
		notifications = []
		pos_configs = self.env['pos.config'].sudo().search([('display_stock', '=', True)])
		if pos_configs:
			ssn_obj = self.env['pos.session'].sudo()
			prod_fields = ssn_obj._loader_params_product_product()['search_params']['fields']
			product = self.with_context(display_default_code=False).search_read([('id', '=', prd_id),('available_in_pos','=',True)],prod_fields)
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
				abc = self.env['bus.bus']._sendmany(notifications)
		return True

	@api.model_create_multi
	def create(self, vals):
		res = super(ProductProduct, self).create(vals)
		for rec in res:
			self.sync_product(rec.id)
		return res

	def write(self, vals):
		res = super(ProductProduct, self).write(vals)
		for i in self:
			i.sync_product(i._origin.id)
		return res

	@api.model
	def create_from_ui(self, product):
		product_id = product.pop('id', False)
		product_get_id = self.browse(product_id)
		if product_id:
			if product_get_id.product_tmpl_id.attribute_line_ids:
				if product.get('list_price') != '':
					if product.get('list_price'):
						product['price_extra'] = product.get('list_price')
						price = product_get_id.list_price
						product['lst_price'] = price + int(product['price_extra'])
					else:
						if product.get('list_price') != 0:
							product['price_extra'] = product.get('list_price').replace(',','.')
						else:
							product['price_extra'] = product.get('list_price')
						AttributePrice = self.env['product.template.attribute.value']
						prices = AttributePrice.search([
							('product_attribute_value_id','in',product_get_id.product_template_attribute_value_ids.ids),
					
						])
						updated = prices.mapped('ptav_product_variant_ids');
						
						len_variant = len(product_get_id.mapped('product_template_attribute_value_ids.price_extra'));
						
						for i in product_get_id.mapped('product_template_attribute_value_ids'):
							divided_price = (int(product['price_extra'])/len_variant);
							i.write({'price_extra' : divided_price});

						product['list_price'] = float(product_get_id.list_price);
				else:
						product['lst_price'] = float(product_get_id.lst_price)
			else:
				if product.get('list_price') != '':
					product['lst_price'] = float(product.get('list_price'))
				else:
					product['lst_price'] = float(product_get_id.lst_price)
		else:
			if product.get('list_price'):
				product['list_price'] = float(product.get('list_price'))
			else:
				product['list_price'] = product.get('list_price').replace(',','.')

		if product.get('cost_price') != '':
			if product.get('cost_price'):
				product['standard_price'] = float(product.get('cost_price'))
			else:
				if product.get('cost_price') != 0:
					product['standard_price'] = product.get('cost_price').replace(',','.')
				else:
					product['standard_price'] = product.get('cost_price')
		else:
			product['standard_price'] = product_get_id.standard_price
		product['available_in_pos'] = True
		if product.get('pos_categ_ids') != False:
			if product.get('pos_categ_ids'):
				product['pos_categ_ids'] = [(6, 0, [product.get('pos_categ_ids')])]
			else:
				product['pos_categ_ids'] = False
		else:
			if product_get_id.pos_categ_ids:
				product['pos_categ_ids'] =int(product_get_id.pos_categ_ids.ids[0])

		if product.get('categ_id') != False:
			if product.get('categ_id'):
				product['categ_id'] = int(product.get('categ_id'))
			else:
				product['categ_id'] = 1
		else:
			product['categ_id'] =int(product_get_id.categ_id.id)

		product['barcode'] = product.get('barcode')
		if product.get('detailed_type'):
			product['detailed_type'] = product.get('detailed_type')


		if ('(') in product.get('display_name'):
			name = product.get('display_name').split('(')
			product['name'] = name[0]
		else:
			product['name'] = product.get('display_name')

		if product.get('default_code'):
			product['default_code'] = product.get('default_code')
			
		str_b = False

		if product.get('image_1920') != None:
			str_b = product.get('image_1920').strip("data:image/png;base64,")
			product['image_1920'] ="i"+str_b
			if product_id:  # Modifying existing product
				if product.get('cost_price') == 0:
					standard_price = product.pop('cost_price',0.0)
					product.update({
						'standard_price' : float(standard_price)
					})
				else:
					cost_value=float(product.get('cost_price'))
					product.update({
						'standard_price' : product.pop('cost_price',cost_value)
					})
				if product.get('pos_categ_ids'):
					product['pos_categ_ids'] = product['pos_categ_ids']
				else:
					product['pos_categ_ids'] = False

				if product['categ_id']:
					product['categ_id'] = int(product['categ_id'])
				else:
					product['categ_id'] = 1

				self.browse(product_id).write(product)
				product_id = self.env['product.product'].browse(product_id)
			else:
				if product.get('detailed_type'):
					prd_type=product.get('detailed_type')
				else:
					prd_type="consu"

				categ_str = ""
				pos_category = self.env['pos.category'].sudo().search([])
				for rec in pos_category:
					if product.get('pos_categ_id'):
						if int(product.get('pos_categ_id')) == rec.id :
							categ_str += rec.name

				product_id = self.create({
					'name':product.get('display_name'),
					'categ_store_fields':categ_str,
					'default_code':product.get('default_code'),
					'available_in_pos' : True,
					'barcode':product.get('barcode'),
					'detailed_type':prd_type,
					'lst_price':float(product.get('list_price',0.0)),
					'standard_price':float(product.get('cost_price')),
					'pos_categ_ids' :[(6, 0, product.get('pos_categ_id'))]  if product.get('pos_categ_id') else False,
					'categ_id' :int(product.get('categ_id')) if int(product.get('categ_id')) else False,
					'taxes_id':[(6, 0, product.get('taxes'))] if product.get('taxes') else False,
					'image_1920':"i"+str_b,
					'active' : True
				})
		else:
			if product_id:  # Modifying existing product
				if product.get('cost_price') == 0:
					standard_price = product.pop('cost_price',0.0)
					product.update({
						'standard_price' : float(standard_price)
					})
				else:
					cost_value=float(product.get('cost_price'))
					product.update({
						'standard_price' : cost_value
					})

				if product['pos_categ_ids']:
					product['pos_categ_ids'] = product['pos_categ_ids']
				else:
					product['pos_categ_ids'] = False

				if product['categ_id']:
					product['categ_id'] = int(product['categ_id'])
				else:
					product['categ_id'] = False
				product.pop('cost_price',0.0)
				self.browse(product_id).write(product)
				product_id = self.env['product.product'].browse(product_id)
			else:
				if product.get('detailed_type'):
					prd_type=product.get('detailed_type')
				else:
					prd_type="consu"
				categ_str = ""
				pos_category = self.env['pos.category'].sudo().search([])
				for rec in pos_category:
					if product.get('pos_categ_id'):
						if int(product.get('pos_categ_id')) == rec.id :
							categ_str += rec.name
				product_id = self.create({
					'name':product.get('display_name'),
					'categ_store_fields':categ_str,
					'default_code':product.get('default_code'),
					'available_in_pos' : True,
					'barcode':product.get('barcode'),
					'detailed_type':prd_type,
					'lst_price':float(product.get('list_price',0.0)),
					'standard_price':float(product.get('cost_price')),
					'pos_categ_ids' :[(6, 0, product.get('pos_categ_id'))] if product.get('pos_categ_id') else False,
					'categ_id' :int(product.get('categ_id')) if int(product.get('categ_id')) else False,
					'taxes_id':[(6, 0, product.get('taxes'))] if product.get('taxes') else False,
					'active' : True
				})
		return int(product_id.id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: