from odoo import models, fields

class SaleOrderType(models.Model):
    _inherit = 'sale.order.type'

    flujo_automatico_ids = fields.Many2many(
        'sale.workflow.process',
        'sale_order_type_workflow_rel',  # Tabla relacional
        'order_type_id',                 # Columna en la tabla relacional que refiere a sale.order.type
        'workflow_id',                   # Columna en la tabla relacional que refiere a sale.workflow.process

        string='Flujos Automáticos',
        help='Seleccione uno o más flujos automáticos para este tipo de pedido',
    )