from odoo import _, api, fields, models
import logging
_logger = logging.getLogger(__name__)

class accountPayment(models.Model):
    _inherit = 'account.payment'
    
    transaction_type = fields.Selection([('internal_transfer', 'Internal Transfer'),
                                         ('customer_payment', 'Customer Payment'),
                                         ('vendor_payment', 'Vendor Payment')])
    
    def set_transaction_type(self):
        if not self.is_internal_transfer:
            if self.payment_type == 'customer':
                self.transaction_type = 'customer_payment'
            self.transaction_type = 'vendor_payment'
        else:
            self.transaction_type = 'internal_transfer'
    