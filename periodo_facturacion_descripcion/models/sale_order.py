# -*- coding: utf-8 -*-
import logging
from odoo import models, api, fields

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'sale.order'

    is_payment_exception_cancel = fields.Boolean(
        string="Cancelar excepción de Contrato",
        default=False)

    def _create_recurring_invoice(self, batch_size=30):
        account_moves = super()._create_recurring_invoice(batch_size)
        all_subscriptions = self.env['sale.order'].search([('is_payment_exception_cancel', '=', True)])
        for subscription in all_subscriptions:
            if subscription.payment_exception:
                subscription.payment_exception = False
        return account_moves
