# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    direccion_por_defecto = fields.Char(
        string='Dirección por defecto',
        default='',
    )

    @api.onchange('partner_id')
    def _onchange_partner_id_direccion_por_defecto(self):
        for comp in self:
            if comp.partner_id and comp.partner_id.street:
                comp.direccion_por_defecto = comp.partner_id.street