# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import models,fields,api,_
from datetime import datetime,timedelta,date
from odoo.tools import float_is_zero



class PosConfigInherit(models.Model):
	_inherit = "pos.config"

	multi_currency = fields.Boolean(string="Enable Multi Currency")
	curr_conv = fields.Boolean(string="Enable Multi Currency Conversation")
	selected_currency = fields.Many2many("res.currency",string= "pos")

	allow_product_variants = fields.Boolean(string="Allow Product Variants")
	allow_selected_close = fields.Selection(
		[('auto_close', 'Allow Auto Close Popup'), ('selected', 'Allow Selected Popup Does not close Popup')],
		string="Allow Selected From Popup", default="auto_close")
	enable_payment_ref = fields.Boolean(string='Enable PayLine Reference')


class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	multi_currency = fields.Boolean(related='pos_config_id.multi_currency', readonly=False)
	curr_conv = fields.Boolean(related='pos_config_id.curr_conv', readonly=False)
	selected_currency = fields.Many2many(related='pos_config_id.selected_currency',readonly=False)

	allow_product_variants = fields.Boolean(related='pos_config_id.allow_product_variants',readonly=False)
	allow_selected_close = fields.Selection(related='pos_config_id.allow_selected_close',readonly=False)

	enable_payment_ref = fields.Boolean(related='pos_config_id.enable_payment_ref',readonly=False)


class CurrencyInherit(models.Model):
	_inherit = "res.currency"

	rate_in_company_currency = fields.Float(compute='_compute_company_currency_rate', string='Company Currency Rate', digits=0)

	def _compute_company_currency_rate(self):
		company = self.env['res.company'].browse(self._context.get('company_id')) or self.env.company
		company_currency = company.currency_id
		for currency in self:
			price = currency.rate
			if company_currency.id != currency.id:
				new_rate = (price)/company_currency.rate
				price = round(new_rate,6)
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
	_name="currency.rate"
	_description = "Exchange Rate"

	currency_id = fields.Many2one("res.currency",string="Currency")
	symbol = fields.Char(related="currency_id.symbol", string="currency symbol")
	date = fields.Datetime(string="current Date",default =datetime.today())
	rate = fields.Float(related="currency_id.rate",string="Exchange Rate")
	pos = fields.Many2one("pos.config")


class ExchangeRate(models.Model):
	_inherit="pos.payment"

	account_currency = fields.Float("Amount currency")
	currency = fields.Char("currency")
	pos_reference = fields.Text(string="PayLine Reference")

class PosPaymentMethod(models.Model):
	_inherit = 'pos.payment.method'

	pos_reference = fields.Text(string="Pos Reference")

class ExchangeRate(models.Model):
	_inherit="account.bank.statement.line"

	account_currency = fields.Monetary("Amount currency")
	currency = fields.Char("currency")


class PosOrder(models.Model):
	_inherit = "pos.order"

	cur_id = fields.Many2one("res.currency")

	@api.model
	def _payment_fields(self, order, ui_paymentline):
		res = super(PosOrder, self)._payment_fields(order, ui_paymentline)
		account_currency = ui_paymentline.get('currency_amount',0)
		if ui_paymentline.get('amount',0) < 0 and  ui_paymentline.get('currency_amount',0) > 0 :
			account_currency = - account_currency
		res.update({
			'account_currency': account_currency if account_currency != 0 else  ui_paymentline.get('amount',0),
			'currency' : ui_paymentline.get('currency_name', order.pricelist_id.currency_id.name),
			'pos_reference': ui_paymentline.get('pos_reference'),
		})
		return res
