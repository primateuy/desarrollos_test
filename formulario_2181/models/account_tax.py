# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.constrains('line_beta')
    def _check_line_beta(self):
        if self.line_beta:
            try:
                int(self.line_beta)
            except:
                raise ValidationError(u"El campo 'Código impuesto 2181' debe ser un número de 3 dígitos")

    line_beta = fields.Char('Código impuesto 2181', size=3)

