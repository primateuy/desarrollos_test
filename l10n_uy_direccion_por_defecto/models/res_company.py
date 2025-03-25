from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    direccion_por_defecto = fields.Char(
        string='Dirección por defecto',
        help='Valor por defecto que se asignará en caso de que la consulta RUT dé error en la Conexión CFE'
    )