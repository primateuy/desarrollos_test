# -*- coding: utf-8 -*-
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'sale.order'

    def _create_recurring_invoice(self, batch_size=30):
        account_moves = super()._create_recurring_invoice(batch_size)
        grouped_invoice = self.env['ir.config_parameter'].get_param('sale_subscription.invoice_consolidation', False)
        all_subscriptions, need_cron_trigger = self._recurring_invoice_get_subscriptions(grouped=grouped_invoice,
                                                                                         batch_size=batch_size)
        for subscription in all_subscriptions:
            if subscription.payment_exception:
                subscription.payment_exception = False
        return account_moves
