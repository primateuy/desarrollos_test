# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import logging
from datetime import timedelta
from functools import partial

import psycopg2
import pytz
import re
from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
import odoo.addons.decimal_precision as dp
from odoo.osv.expression import AND

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
	_inherit = 'pos.order'


	discount_type = fields.Char(string='Discount Type')
	coupon_id = fields.Many2one('pos.gift.coupon',string="Coupon")


	def _export_for_ui(self, order):
		timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
		return {
			'lines': [[0, 0, line] for line in order.lines.export_for_ui()],
			'statement_ids': [[0, 0, payment] for payment in order.payment_ids.export_for_ui()],
			'name': order.pos_reference,
			'uid': re.search('([0-9-]){14}', order.pos_reference).group(0),
			'amount_paid': order.amount_paid,
			'amount_total': order.amount_total,
			'amount_tax': order.amount_tax,
			'amount_return': order.amount_return,
			'pos_session_id': order.session_id.id,
			'pricelist_id': order.pricelist_id.id,
			'partner_id': order.partner_id.id,
			'user_id': order.user_id.id,
			'sequence_number': order.sequence_number,
			'date_order': str(order.date_order.astimezone(timezone)),
			'fiscal_position_id': order.fiscal_position_id.id,
			'to_invoice': order.to_invoice,
			'shipping_date': order.shipping_date,
			'state': order.state,
			'account_move': order.account_move.id,
			'id': order.id,
			'is_tipped': order.is_tipped,
			'tip_amount': order.tip_amount,
			'access_token': order.access_token,
			'ticket_code': order.ticket_code,
			'last_order_preparation_change': order.last_order_preparation_change,
			'discount_type': order.discount_type,
		}

	@api.model
	def _get_invoice_lines_values(self, line_values, pos_order_line):
		return {
			'product_id': line_values['product'].id,
			'quantity': line_values['quantity'],
			'discount': line_values['discount'],
			'price_unit': line_values['price_unit'],
			'name': line_values['name'],
			'tax_ids': [(6, 0, line_values['taxes'].ids)],
			'product_uom_id': line_values['uom'].id,
			'pos_order_line_id' : pos_order_line.id,
			'pos_order_id' : pos_order_line.order_id.id,
			'discount_line_type' : pos_order_line.discount_line_type,
		}

	def _prepare_invoice_vals(self):
		res = super(PosOrder, self)._prepare_invoice_vals()
		res.update({
			'pos_order_id' : self.id,
		})
		return res

	@api.model
	def _amount_line_tax(self, line, fiscal_position_id):
		taxes = line.tax_ids.filtered_domain(self.env['account.tax']._check_company_domain(line.order_id.company_id))
		taxes = fiscal_position_id.map_tax(taxes)
		if line.discount_line_type == 'Percentage':
			price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
		else:
			price = line.price_unit - line.discount
		taxes = taxes.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)['taxes']
		return sum(tax.get('amount', 0.0) for tax in taxes)


	@api.onchange('payment_ids', 'lines')
	def _onchange_amount_all(self):
		for order in self:
			currency = order.pricelist_id.currency_id
			order.amount_paid = sum(payment.amount for payment in order.payment_ids)
			order.amount_return = sum(payment.amount < 0 and payment.amount or 0 for payment in order.payment_ids)
			order.amount_tax = currency.round(sum(self._amount_line_tax(line, order.fiscal_position_id) for line in order.lines))
			amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))
			order.amount_total = order.amount_tax + amount_untaxed


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
		pos_order_id = super()._process_order(order, draft, existing_order)
		order = order['data']
		pos_order = self.env['pos.order'].browse(pos_order_id)
		coupon_id = order.get('coupon_id', False)
		if coupon_id:
			coup_max_amount = order.get('coup_maxamount',False)
			pos_order.write({'coupon_id':  coupon_id})
			pos_order.coupon_id.update({
				'coupon_count': pos_order.coupon_id.coupon_count + 1,
				'max_amount': coup_max_amount
			})
		if pos_order.discount_type and pos_order.discount_type == "Fixed":
				invoice = pos_order.account_move
				for line in invoice.invoice_line_ids : 
					pos_line = line.pos_order_line_id
					if pos_line and pos_line.discount_line_type == "Fixed":
						line.write({'price_unit':pos_line.price_unit})

		return pos_order_id

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
	
class PosOrderLine(models.Model):
	_inherit = 'pos.order.line'

	discount_line_type = fields.Char(string='Discount Type',readonly=True)

	def _export_for_ui(self, orderline):
		return {
			'id': orderline.id,
			'qty': orderline.qty,
			'attribute_value_ids': orderline.attribute_value_ids.ids,
			'custom_attribute_value_ids': orderline.custom_attribute_value_ids.read(
				['id', 'name', 'custom_product_template_attribute_value_id', 'custom_value'], load=False),
			'price_unit': orderline.price_unit,
			'skip_change': orderline.skip_change,
			'uuid': orderline.uuid,
			'price_subtotal': orderline.price_subtotal,
			'price_subtotal_incl': orderline.price_subtotal_incl,
			'product_id': orderline.product_id.id,
			'discount': orderline.discount,
			'tax_ids': [[6, False, orderline.tax_ids.mapped(lambda tax: tax.id)]],
			'pack_lot_ids': [[0, 0, lot] for lot in orderline.pack_lot_ids.export_for_ui()],
			'customer_note': orderline.customer_note,
			'refunded_qty': orderline.refunded_qty,
			'price_extra': orderline.price_extra,
			'full_product_name': orderline.full_product_name,
			'refunded_orderline_id': orderline.refunded_orderline_id.id,
			'combo_parent_id': orderline.combo_parent_id.id,
			'combo_line_ids': orderline.combo_line_ids.mapped('id'),
			'discount_type': orderline.order_id.discount_type
		}

	def _compute_amount_line_all(self):
		self.ensure_one()
		fpos = self.order_id.fiscal_position_id
		tax_ids_after_fiscal_position = fpos.map_tax(self.tax_ids)
		if self.discount_line_type == "Fixed":
			price = self.price_unit - self.discount
		else:
			price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
		taxes = tax_ids_after_fiscal_position.compute_all(price, self.order_id.pricelist_id.currency_id, self.qty,
														  product=self.product_id, partner=self.order_id.partner_id)
		return {'price_subtotal_incl': taxes['total_included'], 'price_subtotal': taxes['total_excluded']}

class PosSession(models.Model):
	_inherit = "pos.session"

	def _pos_ui_models_to_load(self):
		result = super()._pos_ui_models_to_load()
		result += [
			'stock.location',
			'pos.gift.coupon',
			'pos.order'
		]
		return result   

	def _loader_params_pos_order(self):
		return {
			'search_params': {
				'fields': [
					'discount_type',
				],
			}
		}

	def _get_pos_ui_pos_order(self, params):
		return self.env['pos.order'].search_read(**params['search_params'])

	
	def _loader_params_product_product(self):
		result = super(PosSession, self)._loader_params_product_product()
		result['search_params']['fields'].extend(['detailed_type','virtual_available',
					'qty_available','incoming_qty','outgoing_qty','quant_text','is_coupon_product'])
		return result


	def _loader_params_stock_location(self):
		if (self.config_id.show_stock_location == 'specific'):
			return {
				'search_params': {
					'domain': [('id', 'in', self.config_id.stock_location_id.ids)],
					'fields': [
						'id','name',
					],
				}
			}    
		else:
			return {
				'search_params': {
					'domain': [('id', 'in', self.config_id.stock_location_id.ids)],
					'fields': [
						'id','name',
					],
				}
			}
		

	def _get_pos_ui_stock_location(self, params):
		return self.env['stock.location'].search_read(**params['search_params'])
		

	def _loader_params_pos_gift_coupon(self):
		return {
			'search_params': {
				'domain': [], 
				'fields': [
					'name','apply_coupon_on', 'c_barcode', 'user_id', 'issue_date', 'expiry_date',
					'partner_id', 'order_ids', 'active', 'amount', 'description','used','coupon_count', 
					'coupon_apply_times','expiry_date','partner_true','partner_id'
				]
			}
		}

	def _get_pos_ui_pos_gift_coupon(self, params):
		return self.env['pos.gift.coupon'].search_read(**params['search_params'])


class ReportSaleDetailsInherit(models.AbstractModel):
	_inherit = 'report.point_of_sale.report_saledetails'

	def _get_product_total_amount(self, line):

		if line.discount_line_type == 'Percentage':
			return line.currency_id.round(line.price_unit * line.qty * (100 - line.discount) / 100.0)
		else:
			return line.currency_id.round(line.price_unit * line.qty - line.discount)

	def _get_products_and_taxes_dict(self, line, products, taxes, currency):
		key2 = (line.product_id, line.price_unit, line.discount,line.discount_line_type)
		key1 = line.product_id.product_tmpl_id.pos_categ_ids[0].name if len(line.product_id.product_tmpl_id.pos_categ_ids) else _('Not Categorized')
		products.setdefault(key1, {})
		products[key1].setdefault(key2, [0.0, 0.0, 0.0])
		products[key1][key2][0] += line.qty
		products[key1][key2][1] += self._get_product_total_amount(line)
		products[key1][key2][2] += line.price_subtotal
		# products[key1][key2][3] = line.discount_line_type

		if line.tax_ids_after_fiscal_position:
			line_taxes = line.tax_ids_after_fiscal_position.sudo().compute_all(line.price_unit * (1-(line.discount or 0.0)/100.0), currency, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
			base_amounts = {}
			for tax in line_taxes['taxes']:
				taxes.setdefault(tax['id'], {'name': tax['name'], 'tax_amount':0.0, 'base_amount':0.0})
				taxes[tax['id']]['tax_amount'] += tax['amount']
				base_amounts[tax['id']] = tax['base']

			for tax_id, base_amount in base_amounts.items():
				taxes[tax_id]['base_amount'] += base_amount
		else:
			taxes.setdefault(0, {'name': _('No Taxes'), 'tax_amount':0.0, 'base_amount':0.0})
			taxes[0]['base_amount'] += line.price_subtotal_incl
			
		return products, taxes

	@api.model
	def get_sale_details(self, date_start=False, date_stop=False, config_ids=False, session_ids=False):
		""" Serialise the orders of the requested time period, configs and sessions.
		:param date_start: The dateTime to start, default today 00:00:00.
		:type date_start: str.
		:param date_stop: The dateTime to stop, default date_start + 23:59:59.
		:type date_stop: str.
		:param config_ids: Pos Config id's to include.
		:type config_ids: list of numbers.
		:param session_ids: Pos Config id's to include.
		:type session_ids: list of numbers.
		:returns: dict -- Serialised sales.
		"""
		domain = [('state', 'in', ['paid', 'invoiced', 'done'])]
		if (session_ids):
			domain = AND([domain, [('session_id', 'in', session_ids)]])
		else:
			if date_start:
				date_start = fields.Datetime.from_string(date_start)
			else:
				# start by default today 00:00:00
				user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
				today = user_tz.localize(fields.Datetime.from_string(fields.Date.context_today(self)))
				date_start = today.astimezone(pytz.timezone('UTC')).replace(tzinfo=None)

			if date_stop:
				date_stop = fields.Datetime.from_string(date_stop)
				# avoid a date_stop smaller than date_start
				if (date_stop < date_start):
					date_stop = date_start + timedelta(days=1, seconds=-1)
			else:
				# stop by default today 23:59:59
				date_stop = date_start + timedelta(days=1, seconds=-1)

			domain = AND([domain,
				[('date_order', '>=', fields.Datetime.to_string(date_start)),
				('date_order', '<=', fields.Datetime.to_string(date_stop))]
			])

			if config_ids:
				domain = AND([domain, [('config_id', 'in', config_ids)]])

		orders = self.env['pos.order'].search(domain)

		if config_ids:
			config_currencies = self.env['pos.config'].search([('id', 'in', config_ids)]).mapped('currency_id')
		else:
			config_currencies = self.env['pos.session'].search([('id', 'in', session_ids)]).mapped('config_id.currency_id')
		# If all the pos.config have the same currency, we can use it, else we use the company currency
		if config_currencies and all(i == config_currencies.ids[0] for i in config_currencies.ids):
			user_currency = config_currencies[0]
		else:
			user_currency = self.env.company.currency_id

		total = 0.0
		products_sold = {}
		taxes = {}
		refund_done = {}
		refund_taxes = {}
		for order in orders:
			if user_currency != order.pricelist_id.currency_id:
				total += order.pricelist_id.currency_id._convert(
					order.amount_total, user_currency, order.company_id, order.date_order or fields.Date.today())
			else:
				total += order.amount_total
			currency = order.session_id.currency_id

			for line in order.lines:
				if line.qty >= 0:
					products_sold, taxes = self._get_products_and_taxes_dict(line, products_sold, taxes, currency)
				else:
					refund_done, refund_taxes = self._get_products_and_taxes_dict(line, refund_done, refund_taxes, currency)

		taxes_info = self._get_taxes_info(taxes)
		refund_taxes_info = self._get_taxes_info(refund_taxes)

		payment_ids = self.env["pos.payment"].search([('pos_order_id', 'in', orders.ids)]).ids
		if payment_ids:
			self.env.cr.execute("""
				SELECT method.id as id, payment.session_id as session, COALESCE(method.name->>%s, method.name->>'en_US') as name, method.is_cash_count as cash,
					 sum(amount) total, method.journal_id journal_id
				FROM pos_payment AS payment,
					 pos_payment_method AS method
				WHERE payment.payment_method_id = method.id
					AND payment.id IN %s
				GROUP BY method.name, method.is_cash_count, payment.session_id, method.id, journal_id
			""", (self.env.lang, tuple(payment_ids),))
			payments = self.env.cr.dictfetchall()
		else:
			payments = []

		configs = []
		sessions = []
		if config_ids:
			configs = self.env['pos.config'].search([('id', 'in', config_ids)])
			if session_ids:
				sessions = self.env['pos.session'].search([('id', 'in', session_ids)])
			else:
				sessions = self.env['pos.session'].search([('config_id', 'in', configs.ids), ('start_at', '>=', date_start), ('stop_at', '<=', date_stop)])
		else:
			sessions = self.env['pos.session'].search([('id', 'in', session_ids)])
			for session in sessions:
				configs.append(session.config_id)

		for payment in payments:
			payment['count'] = False

		for session in sessions:
			cash_counted = 0
			if session.cash_register_balance_end_real:
				cash_counted = session.cash_register_balance_end_real
			is_cash_method = False
			for payment in payments:
				account_payments = self.env['account.payment'].search([('pos_session_id', '=', session.id)])
				if payment['session'] == session.id:
					if not payment['cash']:
						ref_value = "Closing difference in %s (%s)" % (payment['name'], session.name)
						account_move = self.env['account.move'].search([("ref", "=", ref_value)], limit=1)
						if account_move:
							payment_method = self.env['pos.payment.method'].browse(payment['id'])
							is_loss = any(l.account_id == payment_method.journal_id.loss_account_id for l in account_move.line_ids)
							is_profit = any(l.account_id == payment_method.journal_id.profit_account_id for l in account_move.line_ids)
							payment['final_count'] = payment['total']
							payment['money_difference'] = -account_move.amount_total if is_loss else account_move.amount_total
							payment['money_counted'] = payment['final_count'] + payment['money_difference']
							payment['cash_moves'] = []
							if is_profit:
								move_name = 'Difference observed during the counting (Profit)'
								payment['cash_moves'] = [{'name': move_name, 'amount': payment['money_difference']}]
							elif is_loss:
								move_name = 'Difference observed during the counting (Loss)'
								payment['cash_moves'] = [{'name': move_name, 'amount': payment['money_difference']}]
							payment['count'] = True
						elif payment['id'] in account_payments.mapped('pos_payment_method_id.id'):
							account_payment = account_payments.filtered(lambda p: p.pos_payment_method_id.id == payment['id'])
							payment['final_count'] = payment['total']
							payment['money_counted'] = sum(account_payment.mapped('amount'))
							payment['money_difference'] = payment['money_counted'] - payment['final_count']
							payment['cash_moves'] = []
							if payment['money_difference'] > 0:
								move_name = 'Difference observed during the counting (Profit)'
								payment['cash_moves'] = [{'name': move_name, 'amount': payment['money_difference']}]
							elif payment['money_difference'] < 0:
								move_name = 'Difference observed during the counting (Loss)'
								payment['cash_moves'] = [{'name': move_name, 'amount': payment['money_difference']}]
							payment['count'] = True
					else:
						is_cash_method = True
						previous_session = self.env['pos.session'].search([('id', '<', session.id), ('state', '=', 'closed'), ('config_id', '=', session.config_id.id)], limit=1)
						payment['final_count'] = payment['total'] + previous_session.cash_register_balance_end_real + session.cash_real_transaction
						payment['money_counted'] = cash_counted
						payment['money_difference'] = payment['money_counted'] - payment['final_count']
						cash_moves = self.env['account.bank.statement.line'].search([('pos_session_id', '=', session.id)])
						cash_in_out_list = []
						cash_in_count = 0
						cash_out_count = 0
						if session.cash_register_balance_start > 0:
							cash_in_out_list.append({
								'name': _('Cash Opening'),
								'amount': session.cash_register_balance_start,
							})
						for cash_move in cash_moves:
							if cash_move.amount > 0:
								cash_in_count += 1
								name = f'Cash in {cash_in_count}'
							else:
								cash_out_count += 1
								name = f'Cash out {cash_out_count}'
							if cash_move.move_id.journal_id.id == payment['journal_id']:
								cash_in_out_list.append({
									'name': cash_move.payment_ref if cash_move.payment_ref else name,
									'amount': cash_move.amount
								})
						payment['cash_moves'] = cash_in_out_list
						payment['count'] = True
			if not is_cash_method:
				cash_name = _('Cash') + ' ' + str(session.name)
				payments.insert(0, {
					'name': cash_name,
					'total': 0,
					'final_count': session.cash_register_balance_start,
					'money_counted': session.cash_register_balance_end_real,
					'money_difference': session.cash_register_balance_end_real - session.cash_register_balance_start,
					'cash_moves': [],
					'count': True,
					'session': session.id,
				})
		products = []
		refund_products = []
		for category_name, product_list in products_sold.items():
			category_dictionnary = {
				'name': category_name,
				'products': sorted([{
					'product_id': product.id,
					'product_name': product.name,
					'code': product.default_code,
					'quantity': qty,
					'price_unit': price_unit,
					'discount': discount,
					'discount_line_type' : discount_line_type,
					'uom': product.uom_id.name,
					'total_paid': product_total,
					'base_amount': base_amount,
				} for (product, price_unit, discount, discount_line_type), (qty, product_total, base_amount) in product_list.items()], key=lambda l: l['product_name']),
			}
			products.append(category_dictionnary)
		products = sorted(products, key=lambda l: str(l['name']))
		for category_name, product_list in refund_done.items():
			category_dictionnary = {
				'name': category_name,
				'products': sorted([{
					'product_id': product.id,
					'product_name': product.name,
					'code': product.default_code,
					'quantity': qty,
					'price_unit': price_unit,
					'discount': discount,
					'discount_line_type' : discount_line_type,
					'uom': product.uom_id.name,
					'total_paid': product_total,
					'base_amount': base_amount,
				} for (product, price_unit, discount, discount_line_type), (qty, product_total, base_amount) in product_list.items()], key=lambda l: l['product_name']),
			}
			refund_products.append(category_dictionnary)
		refund_products = sorted(refund_products, key=lambda l: str(l['name']))
		products, products_info = self._get_total_and_qty_per_category(products)
		refund_products, refund_info = self._get_total_and_qty_per_category(refund_products)

		currency = {
			'symbol': user_currency.symbol,
			'position': True if user_currency.position == 'after' else False,
			'total_paid': user_currency.round(total),
			'precision': user_currency.decimal_places,
		}

		session_name = False
		if len(sessions) == 1:
			state = sessions[0].state
			date_start = sessions[0].start_at
			date_stop = sessions[0].stop_at
			session_name = sessions[0].name
		else:
			state = "multiple"

		config_names = []
		for config in configs:
			config_names.append(config.name)

		discount_number = 0
		discount_amount = 0
		invoiceList = []
		totalPaymentsAmount = 0
		invoiceTotal = 0
		for session in sessions:
			discount_number += len(session.order_ids.filtered(lambda o: o.lines.filtered(lambda l: l.discount > 0)))
			discount_amount += session.get_total_discount()
			invoiceList.append({
				'name': session.name,
				'invoices': session._get_invoice_total_list(),
			})
			invoiceTotal += session._get_total_invoice()
			totalPaymentsAmount += session.total_payments_amount

		for payment in payments:
			if payment.get('id'):
				payment['name'] = self.env['pos.payment.method'].browse(payment['id']).name + ' ' + self.env['pos.session'].browse(payment['session']).name

		return {
			'opening_note': sessions[0].opening_notes if len(sessions) == 1 else False,
			'closing_note': sessions[0].closing_notes if len(sessions) == 1 else False,
			'state': state,
			'currency': currency,
			'nbr_orders': len(orders),
			'date_start': date_start,
			'date_stop': date_stop,
			'session_name': session_name if session_name else False,
			'config_names': config_names,
			'payments': payments,
			'company_name': self.env.company.name,
			'taxes': list(taxes.values()),
			'taxes_info': taxes_info,
			'products': products,
			'products_info': products_info,
			'refund_taxes': list(refund_taxes.values()),
			'refund_taxes_info': refund_taxes_info,
			'refund_info': refund_info,
			'refund_products': refund_products,
			'discount_number': discount_number,
			'discount_amount': discount_amount,
			'invoiceList': invoiceList,
			'invoiceTotal': invoiceTotal,
		}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    
