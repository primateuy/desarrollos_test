# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"

    # Activate the currency update
    secondary_currency_id = fields.Many2one(comodel_name='res.currency', string='Divisa secundaria')


class AccountMov(models.Model):
    _inherit = 'account.move'

    def post(self):
        res = super(AccountMov, self).post()
        self.line_ids.compute_amount_secondary()
        return res

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    secondary_currency_id = fields.Many2one(comodel_name='res.currency', string='Divisa secundaria',
                                            related='company_id.secondary_currency_id')
    tipo_cambio = fields.Float(string='TC')
    amount_secondary = fields.Monetary(string='Importe Divisa Secundaria', currency_field='secondary_currency_id')

    def compute_amount_secondary(self):
        for rec in self:
            tipo_cambio = self.env['res.currency.rate'].search([('name', '<=', rec.move_id.date), ('currency_id', '=', self.env.companies.secondary_currency_id.id)],limit=1)
            if tipo_cambio:
                debit_credit = rec.debit or rec.credit
                rec.amount_secondary = debit_credit * tipo_cambio.rate
                rec.tipo_cambio = tipo_cambio.inverse_company_rate
            else:
                rec.amount_secondary = 0
