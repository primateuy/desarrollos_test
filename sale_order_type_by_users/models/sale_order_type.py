from odoo import fields, models, api
from odoo.exceptions import ValidationError


class SaleOrderType(models.Model):
    _inherit = "sale.order.type"

    assignment_method = fields.Selection(
        selection=[
            ("partner", "Por cliente"),
            ("user", "Por usuario"),
        ],
        string="Método de asignación",
        required=True,
        default="partner",
    )

    user_ids = fields.Many2many(
        comodel_name="res.users",
        string="Usuarios predeterminados",
    )
    
    @api.constrains('user_ids')
    def _check_unique_user_assignment(self):
        for record in self:
            for user in record.user_ids:
                other_types = self.search([
                    ('id', '!=', record.id),
                    ('user_ids', 'in', user.id)
                ])
                if other_types:
                    raise ValidationError(
                        f"El usuario {user.name} ya está asignado a otro tipo de orden de venta."
                    )