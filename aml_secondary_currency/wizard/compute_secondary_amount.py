from odoo import models, api, _
from odoo.exceptions import UserError


class ComputeSecondaryAmount(models.TransientModel):
    _name = "compute.secondary.amount"
    _description = "Validate Account Move"

    def compute_secondary_amount(self):
        if self._context.get('active_model') == 'account.move.line':
            domain = [('id', 'in', self._context.get('active_ids', []))]
        else:
            raise UserError('Esta operación debe realizarse desde el menu Apuntes Contables')

        move_lines = self.env['account.move.line'].search(domain)
        if not move_lines:
            raise UserError(_('No se encontaron apuntes'))
        move_lines.compute_amount_secondary()

