from odoo import models, fields


class Callback(models.Model):
    
    _name = 'muk_rest.callback'
    _description = "Callback"
    _rec_name = 'url'
    _order = 'sequence'

    # ----------------------------------------------------------
    # Fields
    # ----------------------------------------------------------

    url = fields.Char(
        string="Callback URL",
        required=True
    )
    
    sequence = fields.Integer(
        string='Sequence',
        required=True,
        default=5
    )
    
    oauth_id = fields.Many2one(
        comodel_name='muk_rest.oauth',
        string="OAuth Configuration",
        ondelete='cascade',
        required=True
    )
    