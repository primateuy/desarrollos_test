from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('type_id')
    def _onchange_type_id_set_workflow(self):
        if self.type_id and self.type_id.flujo_automatico_ids:
            # Si hay varios flujos, se toma el primero (puedes ajustar la lógica si es necesario)
            self.workflow_process_id = self.type_id.flujo_automatico_ids[0].id
        else:
            self.workflow_process_id = False
