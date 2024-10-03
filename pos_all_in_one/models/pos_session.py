# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from datetime import datetime
from odoo.osv.expression import OR

class ProductTemp(models.Model):
	_inherit = 'product.template'

	product_ids = fields.Many2many('product.product', string='Alternative Products',
								   domain=[('available_in_pos', '=', True)])

class POSSession(models.Model):
	_inherit = 'pos.session'


	def _pos_ui_models_to_load(self):
		result = super()._pos_ui_models_to_load()
		result.extend([
			'account.journal',
			'account.move',
			'pos.order',
			'pos.loyalty.setting',
			'pos.redeem.rule',
			'product.template',
			'stock.warehouse',
			'stock.picking.type',
			'stock.location',
			'stock.picking'
		])
		return result

	def _loader_params_pos_category(self):
		res = super(POSSession, self)._loader_params_pos_category()
		fields = res.get('search_params').get('fields')
		fields.append('Minimum_amount')
		res['search_params']['fields'] = fields
		return res

	def _loader_params_res_partner(self):
		res = super(POSSession, self)._loader_params_res_partner()
		fields = res.get('search_params').get('fields')
		fields.extend(['loyalty_points1','loyalty_amount'])
		res['search_params']['fields'] = fields
		return res

	def _loader_params_pos_loyalty_setting(self):
		today_date = datetime.today().date() 
		return {
			'search_params': {
				'domain': [('active','=',True),('issue_date', '<=', today_date ),('expiry_date', '>=', today_date )], 
				'fields': ['name', 'product_id', 'issue_date', 'expiry_date', 'loyalty_basis_on', 'loyality_amount', 'active','redeem_ids']
			}
		}

	def _get_pos_ui_pos_loyalty_setting(self, params):
		return self.env['pos.loyalty.setting'].search_read(**params['search_params'])


	def  _get_pos_ui_pos_redeem_rule(self, params):
		return self.env['pos.redeem.rule'].search_read(**params['search_params'])

	
	def _loader_params_pos_redeem_rule(self):
		return {
			'search_params': {
				'domain': [], 
				'fields': ['reward_amt','min_amt','max_amt','loyality_id']
			}
		}


	def _loader_params_pos_order(self):
		return {
			'search_params': {
				'fields': [
					'is_partial','amount_due',
				],
			}
		}

	def _get_pos_ui_pos_order(self, params):
		return self.env['pos.order'].search_read(**params['search_params'])

	

	def _loader_params_product_product(self):
		res = super(POSSession, self)._loader_params_product_product()
		fields = res.get('search_params').get('fields')
		fields.extend(['type','name','product_template_attribute_value_ids','product_variant_count','product_ids','bi_pos_reports_catrgory'])
		res['search_params']['fields'] = fields
		return res

	def _pos_data_process(self, loaded_data):
		super()._pos_data_process(loaded_data)
		loaded_data['pos_category'] = loaded_data['pos.category']



	def _loader_params_product_template(self):
		return {'search_params': {'domain': [('sale_ok','=',True),('available_in_pos','=',True)], 'fields': ['name','display_name','product_variant_ids','product_variant_count','product_ids']}}

	def _get_pos_ui_product_template(self, params):
		return self.env['product.template'].search_read(**params['search_params'])




	def _loader_params_stock_warehouse(self):
		return {
			'search_params': {
				'domain': [('company_id', '=', self.company_id.id)],
				'fields': ['id','name','display_name','company_id'],
			}
		}

	def _get_pos_ui_stock_warehouse(self, params):
		return self.env['stock.warehouse'].search_read(**params['search_params'])

	def _loader_params_pos_stock_picking_type(self):
		return {
			'search_params': {
			'domain': [('code', '=', 'internal')],
			'fields': ['use_create_lots', 'use_existing_lots','id','name','display_name','code'],
			},
		}

	def _get_pos_ui_pos_stock_picking_type(self, params):
		return self.env['stock.picking.type'].search_read(**params['search_params'])


	def _loader_params_stock_location(self):
		return {
			'search_params': {
				'domain': [('usage', '=', 'internal'),('company_id', '=', self.company_id.id)],
				'fields': ['id','name','display_name'],
			}
		}

	def _get_pos_ui_stock_location(self, params):
		return self.env['stock.location'].search_read(**params['search_params'])

	def _loader_params_stock_picking(self):
		return {
			'search_params': {
				'domain': [],
				'fields': ['id','name','state'],
			}
		}

	def _get_pos_ui_stock_picking(self, params):
		return self.env['stock.picking'].search_read(**params['search_params'])


	def _loader_params_account_move(self):
		return {
			'search_params': {
				'domain': [['move_type','=','out_invoice'], ['state','=','posted'],['payment_state','!=','paid']],
				'fields': [
					'name','partner_id','amount_total','amount_residual','currency_id','amount_residual','state','move_type',
				],
			}
		}

	def _get_pos_ui_account_move(self, params):
		return self.env['account.move'].search_read(**params['search_params'])


	def _loader_params_account_journal(self):
		return {
			'search_params': {
				'domain': [['type','in',['cash','bank']]],
				'fields': [
					'id','name','type',
				],
			}
		}


	def _get_pos_ui_account_journal(self, params):
		return self.env['account.journal'].search_read(**params['search_params'])

	def load_pos_data(self):
		loaded_data = super(POSSession, self).load_pos_data()
		poscurrency = self.env['res.currency'].search_read(
			domain=[('id', 'in', self.config_id.selected_currency.ids)],
			fields=['name','symbol','position','rounding','rate','inverse_rate','rate_in_company_currency'],
		)
		loaded_data['poscurrency'] = poscurrency or loaded_data.get('poscurrency', False)
		pos_session_data=self._get_pos_ui_pos_pos_sessions(self._loader_params_pos_pos_sessions())
		loaded_data['pos_sessions'] = pos_session_data
		pos_stock_picking = self._get_pos_ui_pos_stock_picking_type(self._loader_params_pos_stock_picking_type())
		loaded_data['pos_stock_picking'] = pos_stock_picking
		return loaded_data

	def _loader_params_pos_pos_sessions(self):
		return {
			'search_params': {
				'fields': [
					'id', 'name', 'user_id', 'config_id', 'start_at', 'stop_at', 'sequence_number',
					'payment_method_ids', 'statement_line_ids', 'state', 'update_stock_at_closing'
				],
			},
		}

	def _get_pos_ui_pos_pos_sessions(self, params):
		users = self.env['pos.session'].search_read(**params['search_params'])
		return users


	def _loader_params_res_users(self):
		result = super()._loader_params_res_users()
		result['search_params']['fields'].extend(['company_id','lang','is_allow_numpad','is_allow_payments',
				'is_allow_discount','is_allow_qty','is_edit_price','is_allow_remove_orderline','is_allow_customer_selection',
				'is_allow_plus_minus_button'])
		return result


	def _loader_params_hr_employee(self):
		result = super()._loader_params_hr_employee()
		result['search_params']['fields'].extend(['is_allow_numpad','is_allow_payments','is_allow_discount','is_allow_qty',
			'is_edit_price','is_allow_remove_orderline','is_allow_customer_selection','is_allow_plus_minus_button'])
		return result
