# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _ , tools
from odoo.exceptions import UserError, ValidationError
import psycopg2
import base64
from odoo.http import request
from functools import partial
from odoo.tools import float_is_zero
from operator import itemgetter
from datetime import date, datetime
from collections import defaultdict
from odoo.service.common import exp_version
from odoo.tools import groupby
import logging
_logger = logging.getLogger(__name__)


class PosPaymentInherit(models.Model):
	_inherit = 'pos.payment'

	# session_id = fields.Many2one('pos.session', related='', string='Session', store=True, index=True)

class POSConfigInherit(models.Model):
	_inherit = 'pos.config'
	
	allow_partical_payment = fields.Boolean('Allow Partial Payment')
	partial_product_id = fields.Many2one("product.product",string="Partial Payment Product", domain = [('type', '=', 'service'),('available_in_pos', '=', True)])


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'


	allow_partical_payment = fields.Boolean(related='pos_config_id.allow_partical_payment',readonly=False)
	partial_product_id = fields.Many2one(related='pos_config_id.partial_product_id',readonly=False)


	@api.model_create_multi
	def create(self, vals_list):
		res=super(ResConfigSettings, self).create(vals_list)
		for vals in vals_list:
			product=self.env['product.product'].browse(vals.get('partial_product_id',False))

			if vals.get('allow_partical_payment',False) and product:
				if product.available_in_pos != True:
					raise ValidationError(_('Please enable available in POS for the Partial Payment Product'))

				if product.taxes_id:
					raise ValidationError(_('You are not allowed to add Customer Taxes in the Partial Payment Product'))

		return res


	def write(self, vals):
		res=super(ResConfigSettings, self).write(vals)

		if self.allow_partical_payment:
			if self.partial_product_id.available_in_pos != True:
				raise ValidationError(_('Please enable available in POS for the Partial Payment Product'))

			if self.partial_product_id.taxes_id:
				raise ValidationError(_('You are not allowed to add Customer Taxes in the Partial Payment Product'))

		return res

	

class PosOrderInherit(models.Model):
	_inherit = 'pos.order'

	@api.model
	def _payment_fields(self, order, ui_paymentline):
		res = super(PosOrderInherit, self)._payment_fields(order,ui_paymentline)
		res['session_id'] = order.session_id.id

		return res

	def _default_session(self):
		return self.env['pos.session'].search([('state', '=', 'opened'), ('user_id', '=', self.env.uid)], limit=1)


	is_picking_created = fields.Boolean('Picking Created')
	is_partial = fields.Boolean('Is Partial Payment')
	amount_due = fields.Float("Amount Due",compute="get_amount_due")

	@api.depends('amount_total','amount_paid')
	def get_amount_due(self):
		for order in self :
			if order.amount_paid - order.amount_total >= 0:
				order.amount_due = 0
				order.is_partial = False
			else:
				order.amount_due = order.amount_total - order.amount_paid
				
	def write(self, vals):
		for order in self:
			if order.name == '/' and order.is_partial :
				vals['name'] = order.config_id.sequence_id._next()
		return super(PosOrderInherit, self).write(vals)

	# def _is_pos_order_paid(self):
	# 	return float_is_zero(self._get_rounded_amount(self.amount_total) - self.amount_paid, precision_rounding=self.currency_id.rounding)

	# def action_pos_order_paid(self):
	# 	self.ensure_one()
	# 	if not self.is_partial:
	# 		return super(PosOrderInherit, self).action_pos_order_paid()

	# 	if self.is_partial:
	# 		if self._is_pos_order_paid():
	# 			self.write({'state': 'paid'})
	# 			if self.picking_ids:
	# 				return True
	# 			else :
	# 				return self._create_order_picking()
	# 		else:
	# 			if not self.picking_ids :
	# 				return self._create_order_picking()
	# 			else:
	# 				return False

	@api.model
	def _order_fields(self, ui_order):
		res = super(PosOrderInherit, self)._order_fields(ui_order)
		process_line = partial(self.env['pos.order.line']._order_line_fields, session_id=ui_order['pos_session_id'])
		if 'is_partial' in ui_order:
			res['is_partial'] = ui_order.get('is_partial',False) 
			res['amount_due'] = ui_order.get('amount_due',0.0) 
		return res

	@api.model
	def _process_order(self, order, draft, existing_order):
		"""Create or update an pos.order from a given dictionary.

		:param dict order: dictionary representing the order.
		:param bool draft: Indicate that the pos_order is not validated yet.
		:param existing_order: order to be updated or False.
		:type existing_order: pos.order.
		:returns: id of created/updated pos.order
		:rtype: int
		"""
		order_data = order['data']
		is_partial = order_data.get('is_partial')
		is_paying_partial = order_data.get('is_paying_partial', False)

		pos_order = False
		if not is_partial and not is_paying_partial:
			pos_order_id  = super()._process_order(order, draft, existing_order)
			pos_order = self.env['pos.order'].browse(pos_order_id)
		else:
			pos_session = self.env['pos.session'].browse(order_data['pos_session_id'])
			if pos_session.state == 'closing_control' or pos_session.state == 'closed':
				order_data['pos_session_id'] = self._get_valid_session(order_data).id
			if is_paying_partial:
				pos_order = self.search([('pos_reference', '=', order_data.get('name'))])
			elif is_partial:
				pos_order = self.create(self._order_fields(order_data))
			pos_order = pos_order.with_company(pos_order.company_id)
			self = self.with_company(pos_order.company_id)
			self._process_payment_lines(order_data, pos_order, pos_session, draft)
			if not pos_order.check_partial_state(order_data):
				return pos_order.id
			pos_order._create_order_picking()
			if pos_order.to_invoice and pos_order.state == 'paid':
				pos_order.action_pos_order_invoice()

		# if pos_order:
		# 	coupon_id = order.get('coupon_id', False)
		# 	if coupon_id:
		# 		coup_max_amount = order.get('coup_maxamount',False)
		# 		pos_order.write({'coupon_id':  coupon_id})
		# 		pos_order.coupon_id.update({
		# 			'coupon_count': pos_order.coupon_id.coupon_count + 1,
		# 			'max_amount': coup_max_amount
		# 		})

		# 	if pos_order.discount_type and pos_order.discount_type == "Fixed":
		# 		invoice = pos_order.account_move
		# 		for line in invoice.invoice_line_ids : 
		# 			pos_line = line.pos_order_line_id
		# 			if pos_line and pos_line.discount_line_type == "Fixed":
		# 				line.write({'price_unit':pos_line.price_unit})

		return pos_order.id

	def check_partial_state(self,order):
		self.ensure_one()

		if not self.config_id.cash_rounding \
		   or self.config_id.only_round_cash_method \
		   and not any(p.payment_method_id.is_cash_count for p in self.payment_ids):
			total = self.amount_total
		else:
			total = float_round(self.amount_total, precision_rounding=self.config_id.rounding_method.rounding, rounding_method=self.config_id.rounding_method.rounding_method)
		
		isPaid = float_is_zero(total - self.amount_paid, precision_rounding=self.currency_id.rounding)
		if not isPaid and not self.config_id.cash_rounding:
			return False
		elif not isPaid and self.config_id.cash_rounding:
			currency = self.currency_id
			if self.config_id.rounding_method.rounding_method == "HALF-UP":
				maxDiff = currency.round(self.config_id.rounding_method.rounding / 2)
			else:
				maxDiff = currency.round(self.config_id.rounding_method.rounding)

			diff = currency.round(self.amount_total - self.amount_paid)
			if not abs(diff) <= maxDiff:
				return False

		self.write({'state': 'paid', 'to_invoice' : order.get('to_invoice')})

		return True


	@api.model_create_multi
	def create(self, vals_list):
		orders = super().create(vals_list)
		for pos_order in orders:
			if pos_order.config_id.discount_type == 'percentage':
				pos_order.update({'discount_type': "Percentage"})
				pos_order.lines.update({'discount_line_type': "Percentage"})
			if pos_order.config_id.discount_type == 'fixed':
				pos_order.update({'discount_type': "Fixed"})
				pos_order.lines.update({'discount_line_type': "Fixed"})

		return orders
		
	# def _create_order_picking(self):

	# 	if self.is_partial:
	# 		return True
	# 	else:
	# 		return super()._create_order_picking()


	def _process_payment_lines(self, pos_order, order, pos_session, draft):
		"""Create account.bank.statement.lines from the dictionary given to the parent function.

		If the payment_line is an updated version of an existing one, the existing payment_line will first be
		removed before making a new one.
		:param pos_order: dictionary representing the order.
		:type pos_order: dict.
		:param order: Order object the payment lines should belong to.
		:type order: pos.order
		:param pos_session: PoS session the order was created in.
		:type pos_session: pos.session
		:param draft: Indicate that the pos_order is not validated yet.
		:type draft: bool.
		"""
		prec_acc = order.currency_id.decimal_places
		is_paying_partial = pos_order.get('is_paying_partial')
		is_partial = pos_order.get('is_partial')
		if not is_paying_partial:
			order._clean_payment_lines()
		order_bank_statement_lines= self.env['pos.payment'].search([('pos_order_id', '=', order.id)])
		if not is_paying_partial:
			order_bank_statement_lines.unlink()
		for payments in pos_order['statement_ids']:
			order.add_payment(self._payment_fields(order, payments[2]))
		order.amount_paid = sum(order.payment_ids.mapped('amount'))
		if order.amount_paid >= order.amount_total :
			order.write({
				'is_partial' : False,
			})

		if not draft and not float_is_zero(pos_order['amount_return'], prec_acc):
			cash_payment_method = pos_session.payment_method_ids.filtered('is_cash_count')[:1]
			if not cash_payment_method:
				raise UserError(_("No cash statement found for this session. Unable to record returned cash."))
				
			return_amount = pos_order.get('amount_return',0)
			sc = order.pricelist_id.currency_id
			if  pos_order.get('currency_amount') and pos_order.get('currency_symbol'):
				oc = self.env['res.currency'].search([('name','=',pos_order.get('currency_name',''))])
				if oc != sc:
					return_amount = sc._convert(pos_order.get('amount_return',0), oc, order.company_id, order.date_order)

			return_payment_vals = {
				'name': _('return'),
				'pos_order_id': order.id,
				'session_id': order.session_id.id,
				'amount': -pos_order['amount_return'],
				'payment_date': fields.Datetime.now(),
				'payment_method_id': cash_payment_method.id,
				'account_currency': -return_amount or 0.0,
				'currency' : pos_order.get('currency_name',order.pricelist_id.currency_id.name),
				'is_change': True,
			}
			order.add_payment(return_payment_vals)

class PosSessionInherit(models.Model):
	_inherit = 'pos.session'

	def _pos_data_process(self, loaded_data):
		"""
		This is where we need to process the data if we can't do it in the loader/getter
		"""
		def filter_taxes_on_company(product_taxes, taxes_by_company):
			"""
			Filter the list of tax ids on a single company starting from the current one.
			If there is no tax in the result, it's filtered on the parent company and so
			on until a non empty result is found.
			"""
			taxes, comp = None, self.company_id
			while not taxes and comp:
				taxes = list(set(product_taxes) & set(taxes_by_company[comp.id]))
				comp = comp.parent_id
			return taxes

		loaded_data['version'] = exp_version()

		loaded_data['units_by_id'] = {unit['id']: unit for unit in loaded_data['uom.uom']}

		loaded_data['taxes_by_id'] = {tax['id']: tax for tax in loaded_data['account.tax']}
		for tax in loaded_data['taxes_by_id'].values():
			tax['children_tax_ids'] = [loaded_data['taxes_by_id'][id] for id in tax['children_tax_ids']]

		taxes_by_company = defaultdict(set)
		# If the current company is a branch company, the taxes of the products can come
		# from the branch and its parents.
		# We have to make sure to not mix them together and only use the taxes from the
		# parent if there is no tax from the branch.
		if self.company_id.parent_id:
			# group all taxes by company in a dict where:
			# - key: ID of the company
			# - values: list of tax ids
			key_company_id = itemgetter('company_id')
			key_id = itemgetter('id')
			for key, group in groupby(loaded_data['account.tax'], key=key_company_id):
				taxes_by_company[key[0]] = list(map(key_id, group))
		if len(taxes_by_company) > 1:
			for product in loaded_data['product.product']:
				if len(product['taxes_id']) > 1:
					product['taxes_id'] = filter_taxes_on_company(product['taxes_id'], taxes_by_company)

		if self.config_id.use_pricelist:
			default_pricelist = next(
				(pl for pl in loaded_data['product.pricelist'] if pl['id'] == self.config_id.pricelist_id.id),
				False
			)
			if default_pricelist:
				loaded_data['default_pricelist'] = default_pricelist

		fiscal_position_by_id = {fpt['id']: fpt for fpt in self._get_pos_ui_account_fiscal_position_tax(
			self._loader_params_account_fiscal_position_tax())}
		for fiscal_position in loaded_data['account.fiscal.position']:
			fiscal_position['fiscal_position_taxes_by_id'] = {tax_id: fiscal_position_by_id[tax_id] for tax_id in fiscal_position['tax_ids']}

		loaded_data['attributes_by_ptal_id'] = self._get_attributes_by_ptal_id()
		loaded_data['base_url'] = self.get_base_url()
		loaded_data['pos_has_valid_product'] = self._pos_has_valid_product()
		loaded_data['pos_special_products_ids'] = self.env['pos.config']._get_special_products().ids
		loaded_data['open_orders'] = self.env['pos.order'].search([('session_id', '=', self.id), ('state', '=', 'draft'),('is_partial','=',False)]).export_for_ui()
		loaded_data['partner_commercial_fields'] = self.env['res.partner']._commercial_fields()
		loaded_data['show_product_images'] = self.env['ir.config_parameter'].sudo().get_param('point_of_sale.show_product_images', 'yes')
		loaded_data['show_category_images'] = self.env['ir.config_parameter'].sudo().get_param('point_of_sale.show_category_images', 'yes')
		
	@api.model
	def _pos_ui_models_to_load(self):
		result = super()._pos_ui_models_to_load()
		new_model = 'pos.order'
		if new_model not in result:
			result.append(new_model)
		return result

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

	@api.model_create_multi
	def create(self, vals):
		res = super(PosSessionInherit, self).create(vals)
		uid = request.env.uid if request else self.env.uid
		orders = self.env['pos.order'].search([('user_id', '=', uid),
			('state', '=', 'draft'),('session_id.state', '=', 'closed')])
		orders.write({'session_id': res.id})
		return res

	def _check_if_no_draft_orders(self):
		draft_orders = self.order_ids.filtered(lambda order: order.state == 'draft')
		do = []
		for i in draft_orders:
			if not i.is_partial:
				do.append(i.name)
		if do:
			raise UserError(_(
				'There are still orders in draft state in the session. '
				'Pay or cancel the following orders to validate the session:\n%s'
			) % ', '.join(do)
							)
		return True

	def _get_closed_orders(self):
		return self.order_ids.filtered(lambda o: o.is_partial == False and o.state not in ['draft', 'cancel'])

	def _create_picking_at_end_of_session(self):
		self.ensure_one()
		lines_grouped_by_dest_location = {}
		picking_type = self.config_id.picking_type_id

		if not picking_type or not picking_type.default_location_dest_id:
			session_destination_id = self.env['stock.warehouse']._get_partner_locations()[0].id
		else:
			session_destination_id = picking_type.default_location_dest_id.id

		for order in self._get_closed_orders():
			if order.is_picking_created == False:
				if order.company_id.anglo_saxon_accounting and order.is_invoiced or order.shipping_date:
					continue
				destination_id = order.partner_id.property_stock_customer.id or session_destination_id
				if destination_id in lines_grouped_by_dest_location:
					lines_grouped_by_dest_location[destination_id] |= order.lines
				else:
					lines_grouped_by_dest_location[destination_id] = order.lines

			if order.is_partial:
				order.write({
						'is_picking_created':True
					})

		for location_dest_id, lines in lines_grouped_by_dest_location.items():
			pickings = self.env['stock.picking']._create_picking_from_pos_order_lines(location_dest_id, lines, picking_type)
			pickings.write({'pos_session_id': self.id, 'origin': self.name})

	def action_pos_session_closing_control(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
		bank_payment_method_diffs = bank_payment_method_diffs or {}
		for session in self:
			orders = session.order_ids.filtered(lambda order: order.is_partial == False)
			if any(order.state == 'draft' for order in orders):
				raise UserError(_("You cannot close the POS when orders are still in draft"))
			if session.state == 'closed':
				raise UserError(_('This session is already closed.'))
			stop_at = self.stop_at or fields.Datetime.now()
			session.write({'state': 'closing_control', 'stop_at': stop_at})
			if not session.config_id.cash_control:
				return session.action_pos_session_close(balancing_account, amount_to_balance, bank_payment_method_diffs)
			# If the session is in rescue, we only compute the payments in the cash register
			# It is not yet possible to close a rescue session through the front end, see `close_session_from_ui`
			if session.rescue and session.config_id.cash_control:
				default_cash_payment_method_id = self.payment_method_ids.filtered(lambda pm: pm.type == 'cash')[0]
				orders = self._get_closed_orders()
				total_cash = sum(
					orders.payment_ids.filtered(lambda p: p.payment_method_id == default_cash_payment_method_id).mapped('amount')
				) + self.cash_register_balance_start

				session.cash_register_balance_end_real = total_cash

			return session.action_pos_session_validate(balancing_account, amount_to_balance, bank_payment_method_diffs)

	def get_closing_control_data(self):
		if not self.env.user.has_group('point_of_sale.group_pos_user'):
			raise AccessError(_("You don't have the access rights to get the point of sale closing control data."))
		self.ensure_one()
		order = self.order_ids.filtered(lambda o: o.state == 'paid' or o.state == 'invoiced')
		orders = order + self.order_ids.filtered(lambda o: o.is_partial == True)
		payments = orders.payment_ids.filtered(lambda p: p.payment_method_id.type != "pay_later")
		# payments = payment.filtered(lambda p: p.session_id in self.ids)
		pay_later_payments = orders.payment_ids - payments
		cash_payment_method_ids = self.payment_method_ids.filtered(lambda pm: pm.type == 'cash')
		default_cash_payment_method_id = cash_payment_method_ids[0] if cash_payment_method_ids else None
		total_default_cash_payment_amount = sum(payments.filtered(lambda p: p.session_id.id in self.ids and p.payment_method_id == default_cash_payment_method_id).mapped('amount')) if default_cash_payment_method_id else 0
		other_payment_method_ids = self.payment_method_ids - default_cash_payment_method_id if default_cash_payment_method_id else self.payment_method_ids
		cash_in_count = 0
		cash_out_count = 0
		cash_in_out_list = []
		last_session = self.search([('config_id', '=', self.config_id.id), ('id', '!=', self.id)], limit=1)
		for cash_move in self.sudo().statement_line_ids.sorted('create_date'):
			if cash_move.amount > 0:
				cash_in_count += 1
				name = f'Cash in {cash_in_count}'
			else:
				cash_out_count += 1
				name = f'Cash out {cash_out_count}'
			cash_in_out_list.append({
				'name': cash_move.payment_ref if cash_move.payment_ref else name,
				'amount': cash_move.amount
			})

		final_data= {
			'orders_details': {
				'quantity': len(orders),
				'amount': sum(orders.mapped('amount_total'))
			},
			'opening_notes': self.opening_notes,
			'default_cash_details': {
				'name': default_cash_payment_method_id.name,
				'amount': last_session.cash_register_balance_end_real + total_default_cash_payment_amount +
											 sum(self.statement_line_ids.mapped('amount')),
				'opening': last_session.cash_register_balance_end_real,
				'payment_amount': total_default_cash_payment_amount,
				'moves': cash_in_out_list,
				'id': default_cash_payment_method_id.id
			} if default_cash_payment_method_id else None,
			'other_payment_methods': [{
				'name': pm.name,
				'amount': sum(orders.payment_ids.filtered(lambda p: p.session_id.id in self.ids and p.payment_method_id == pm).mapped('amount')),
				'number': len(orders.payment_ids.filtered(lambda p: p.payment_method_id == pm)),
				'id': pm.id,
				'type': pm.type,
			} for pm in other_payment_method_ids],
			'is_manager': self.user_has_groups("point_of_sale.group_pos_manager"),
			'amount_authorized_diff': self.config_id.amount_authorized_diff if self.config_id.set_maximum_difference else None
		}
		return final_data

	def _cannot_close_session(self, bank_payment_method_diffs=None):
		"""
		Add check in this method if you want to return or raise an error when trying to either post cash details
		or close the session. Raising an error will always redirect the user to the back end.
		It should return {'successful': False, 'message': str, 'redirect': bool} if we can't close the session
		"""
		bank_payment_method_diffs = bank_payment_method_diffs or {}
		orders = self.order_ids.filtered(lambda order: order.is_partial == False)
		if any(order.state == 'draft' for order in orders):
			return {'successful': False, 'message': _("You cannot close the POS when orders are still in draft"), 'redirect': False}
		if self.state == 'closed':
			return {
				'successful': False,
				'type': 'alert',
				'title': 'Session already closed',
				'message': _("The session has been already closed by another User. "
							"All sales completed in the meantime have been saved in a "
							"Rescue Session, which can be reviewed anytime and posted "
							"to Accounting from Point of Sale's dashboard."),
				'redirect': True
			}
		if bank_payment_method_diffs:
			no_loss_account = self.env['account.journal']
			no_profit_account = self.env['account.journal']
			for payment_method in self.env['pos.payment.method'].browse(bank_payment_method_diffs.keys()):
				journal = payment_method.journal_id
				compare_to_zero = self.currency_id.compare_amounts(bank_payment_method_diffs.get(payment_method.id), 0)
				if compare_to_zero == -1 and not journal.loss_account_id:
					no_loss_account |= journal
				elif compare_to_zero == 1 and not journal.profit_account_id:
					no_profit_account |= journal
			message = ''
			if no_loss_account:
				message += _("Need loss account for the following journals to post the lost amount: %s\n", ', '.join(no_loss_account.mapped('name')))
			if no_profit_account:
				message += _("Need profit account for the following journals to post the gained amount: %s", ', '.join(no_profit_account.mapped('name')))
			if message:
				return {'successful': False, 'message': message, 'redirect': False}


class PosMakePayment(models.TransientModel):
	_inherit = 'pos.make.payment'

	def check(self):
		"""Check the order:
		if the order is not paid: continue payment,
		if the order is paid print ticket.
		"""
		self.ensure_one()
		order = self.env['pos.order'].browse(self.env.context.get('active_id', False))
		if self.payment_method_id.split_transactions and not order.partner_id:
			raise UserError(_(
				"Customer is required for %s payment method.",
				self.payment_method_id.name
			))
		currency = order.currency_id

		init_data = self.read()[0]
		payment_method = self.env['pos.payment.method'].browse(init_data['payment_method_id'][0])
		if not float_is_zero(init_data['amount'], precision_rounding=currency.rounding):
			order.add_payment({
				'pos_order_id': order.id,
				'session_id' : order.session_id.id,
				'amount': order._get_rounded_amount(init_data['amount'], payment_method.is_cash_count or not self.config_id.only_round_cash_method),
				'name': init_data['payment_name'],
				'payment_method_id': init_data['payment_method_id'][0],
			})

		"""
			Refund Functionality
		"""
		if order.refunded_order_ids:
			for r_line in order.lines:
				po_line_obj = self.env['pos.order.line']
				rm_line = po_line_obj.browse(r_line.id)	
				for m_order in order.refunded_order_ids : 
					main_order=self.env['pos.order'].browse(m_order.id)
					for l in main_order.lines:
						line = po_line_obj.browse(l.id)
						if line:
							line.write({
								'return_qty' : line.return_qty - rm_line.qty,
							})	
		if order.is_partial == True:
			if order._is_pos_order_paid():
				order.action_pos_order_paid()
				order._compute_total_cost_in_real_time()
				return {'type': 'ir.actions.act_window_close'}
		
		if order.state == 'draft' and order._is_pos_order_paid():
			order._process_saved_order(False)
			if order.state in {'paid', 'done', 'invoiced'}:
				order._send_order()
			return {'type': 'ir.actions.act_window_close'}
		return self.launch_payment()