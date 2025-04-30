# -*- coding: utf-8 -*-
from odoo import models, fields

class SaleSubscriptionPlan(models.Model):
    _inherit = 'sale.subscription.plan'

    usar_descripcion_cotizacion = fields.Boolean(
        string="Usar descripción de cotización",
        default=True,
        help="Si se activa, la factura usará únicamente la descripción original de la cotización sin concatenar datos de la recurrencia."
    )

    descartar_devengamiento = fields.Boolean(
        string="Descartar devengamiento",
        default=False,
        help="Si se activa, al generar facturas en borrador se dejarán en blanco las fechas desde y hasta del renglón de factura."
    )
