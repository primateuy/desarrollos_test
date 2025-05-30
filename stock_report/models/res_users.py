from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    warehouse_ids = fields.Many2many('stock.warehouse', string="Almacenes permitidos")