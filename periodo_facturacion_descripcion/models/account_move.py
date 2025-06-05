# -*- coding: utf-8 -*-
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model_create_multi
    def create(self, vals_list):
        # Crear facturas (borrador)
        invoices = super().create(vals_list)

        # Limpiar deferred_* si el plan lo requiere
        for inv in invoices:
            for line in inv.invoice_line_ids:
                # Se verifica que la línea de factura tenga relacionada alguna línea de venta
                if line.sale_line_ids and line.sale_line_ids[0].order_id.plan_id.usar_descripcion_cotizacion:
                    sale_line = line.sale_line_ids[0]
                    original_description = sale_line.name or ''
                    line.write({'name': original_description})
                if line.sale_line_ids and line.sale_line_ids[0].order_id.plan_id.descartar_devengamiento:
                    line.write({
                        'deferred_start_date': False,
                        'deferred_end_date': False,
                    })

        return invoices
