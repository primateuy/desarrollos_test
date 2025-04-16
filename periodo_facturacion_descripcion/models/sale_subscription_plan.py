from odoo import models, fields

class SaleSubscriptionPlan(models.Model):
    _inherit = 'sale.subscription.plan'

    usar_descripcion_cotizacion = fields.Boolean(
        string="Usar descripción de cotización",
        default=True,
        help="Si se activa, la factura usará únicamente la descripción original de la cotización sin concatenar datos de la recurrencia."
    )
