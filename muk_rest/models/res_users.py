from odoo import models, fields


class ResUsers(models.Model):
    
    _inherit = 'res.users'

    # ----------------------------------------------------------
    # Properties
    # ----------------------------------------------------------
    
    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + [
            'oauth1_session_ids',
            'oauth2_session_ids',
        ]

    # ----------------------------------------------------------
    # Fields
    # ----------------------------------------------------------
    
    oauth1_session_ids = fields.One2many(
        comodel_name='muk_rest.access_token',
        inverse_name='user_id',
        domain="[('user_id', '=', uid)]",
        string="OAuth1 Sessions",
        readonly=True,
    )
    
    oauth2_session_ids = fields.One2many(
        comodel_name='muk_rest.bearer_token',
        inverse_name='user_id',
        domain="""
            [
                '&', 
                ('user_id', '=', uid), 
                '|', 
                ('expiration_date', '=', False), 
                ('expiration_date', '>', context_today())
            ]
        """,
        string="OAuth2 Sessions",
        readonly=True,
    )
