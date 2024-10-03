# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.tools import float_is_zero
from odoo.exceptions import ValidationError, UserError

class PosConfigInherit(models.Model):
	_inherit = "pos.config"

	multi_currency = fields.Boolean(string="Enable Multi Currency")
	curr_conv = fields.Boolean(string="Enable Multi Currency Conversation")
	selected_currency = fields.Many2many("res.currency", "pos_multi_currency_rel",  string="pos")


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	pos_multi_currency = fields.Boolean(related='pos_config_id.multi_currency',readonly=False)
	pos_curr_conv = fields.Boolean(related='pos_config_id.curr_conv',readonly=False)
	pos_selected_currency = fields.Many2many(related='pos_config_id.selected_currency', readonly=False)


class CurrencyInherit(models.Model):
	_inherit = "res.currency"

	rate_in_company_currency = fields.Float(compute='_compute_company_currency_rate', string='Company Currency Rate',
											digits=0)

	def _compute_company_currency_rate(self):
		company = self.env['res.company'].browse(self._context.get('company_id')) or self.env.company
		company_currency = company.currency_id
		for currency in self:
			price = currency.rate
			if company_currency.id != currency.id:
				new_rate = (price) / company_currency.rate
				price = round(new_rate, 6)
			else:
				price = 1
			currency.rate_in_company_currency = price

	@api.depends('rate_ids.rate')
	@api.depends_context('to_currency', 'date', 'company', 'company_id')
	def _compute_current_rate(self):
		date = self._context.get('date') or fields.Date.context_today(self)
		company = self.env['res.company'].browse(self._context.get('company_id')) or self.env.company
		company = company.root_id
		to_currency = self.browse(self.env.context.get('to_currency')) or company.currency_id
		# the subquery selects the last rate before 'date' for the given currency/company
		currency_rates = (self + to_currency)._get_rates(self.env.company, date)
		for currency in self:
			currency.rate = currency_rates.get(currency._origin.id) / currency_rates.get(to_currency.id)
			currency.inverse_rate = 1 / currency.rate
			if currency != company.currency_id:
				currency.rate_string = '1 %s = %.6f %s' % (to_currency.name, currency.rate, currency.name)
			else:
				currency.rate_string = ''



class ExchangeRate(models.Model):
	_name = "currency.rate"
	_description = "Exchange Rate"

	currency_id = fields.Many2one("res.currency", string="Currency")
	symbol = fields.Char(related="currency_id.symbol", string="currency symbol")
	date = fields.Datetime(string="current Date", default=datetime.today())
	rate = fields.Float(related="currency_id.rate", string="Exchange Rate")
	pos = fields.Many2one("pos.config")


class ExchangeRate(models.Model):
	_inherit = "pos.payment"

	account_currency = fields.Float("Amount currency")
	currency_name = fields.Char("currency")


class ExchangeRate(models.Model):
	_inherit = "account.bank.statement.line"

	account_currency = fields.Monetary("Amount currency")
	currency_name = fields.Char("currency")


class PosOrder(models.Model):
	_inherit = "pos.order"

	cur_id = fields.Many2one("res.currency")


	@api.model
	def _payment_fields(self, order, ui_paymentline):
		fields = super(PosOrder, self)._payment_fields(order, ui_paymentline)
		account_currency = ui_paymentline.get('currency_amount',0)
		if ui_paymentline.get('amount',0) < 0 and  ui_paymentline.get('currency_amount',0) > 0 :
			account_currency = - account_currency
		fields.update({
			'account_currency': account_currency if account_currency != 0 else  ui_paymentline.get('amount',0),
			'currency_name' : ui_paymentline['currency_name'] if ui_paymentline.get('currency_name') else order.pricelist_id.currency_id.name,
		})

		return fields

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

		order._clean_payment_lines()
		for payments in pos_order['statement_ids']:
			order.add_payment(self._payment_fields(order, payments[2]))

		order.amount_paid = sum(order.payment_ids.mapped('amount'))

		if not draft and not float_is_zero(pos_order['amount_return'], prec_acc):
			cash_payment_method = pos_session.payment_method_ids.filtered('is_cash_count')[:1]
			if not cash_payment_method:
				raise UserError(_("No cash statement found for this session. Unable to record returned cash."))


			return_amount = 0
			sc = order.currency_id
			if  pos_order.get('currency_amount') and pos_order.get('currency_symbol'):
				oc = self.env['res.currency'].search([('name','=',pos_order.get('currency_name',''))])
				if oc != sc:
					return_amount = sc._convert(pos_order.get('amount_return',0), oc, order.company_id, order.date_order)


			return_payment_vals = {
				'name': _('return'),
				'pos_order_id': order.id,
				'amount': -pos_order['amount_return'],
				'payment_date': fields.Datetime.now(),
				'payment_method_id': cash_payment_method.id,
				'is_change': True,
				'account_currency': -return_amount or 0.0,
				'currency_name' : pos_order.get('currency_name',order.pricelist_id.currency_id.name),
			}
			order.add_payment(return_payment_vals)


class POSSession(models.Model):
	_inherit = 'pos.session'

	def load_pos_data(self):
		loaded_data = super(POSSession, self).load_pos_data()
		poscurrency = self.env['res.currency'].search_read(
			domain=[('id', 'in', self.config_id.selected_currency.ids)],
			fields=['name','symbol','position','rounding','rate','rate_in_company_currency','inverse_rate'],
		)
		loaded_data['poscurrency'] = poscurrency
		return loaded_data