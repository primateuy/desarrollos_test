# -*- coding: utf-8 -*-

from odoo import models, api

class OrdenVenta(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        """ Extiende el botón Confirmar para ejecutar trabajos automáticos """
        # Ejecutamos la lógica original de Odoo
        resultado = super(OrdenVenta, self).action_confirm()

        # Ejecutamos los trabajos automáticos (cron jobs) manualmente
        trabajos_cron = self.env['ir.cron'].search([('state', '=', 'code')])
        for trabajo in trabajos_cron:
            trabajo.method_direct_trigger()  # Ejecuta la tarea programada en ir.cron
        
        return resultado
