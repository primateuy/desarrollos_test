# -*- coding: utf-8 -*-
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'sale.order'

    def _create_recurring_invoice(self, batch_size=30):
        account_moves = super()._create_recurring_invoice(batch_size)
        all_subscriptions = self.env['sale.order'].search([('payment_exception', '=', True)])
        for subscription in all_subscriptions:
            if subscription.payment_exception:
                subscription.payment_exception = False
        return account_moves
