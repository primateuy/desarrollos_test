from odoo import models, _
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def unlink(self):
        if not self.env.user.has_group('control_eliminacion_de_pagos.group_allow_delete_payment'):
            raise UserError(_("No tiene permisos para eliminar pagos."))
        return super().unlink()