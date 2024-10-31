from odoo import _, models, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.muk_rest.tools import common


class OAuth2(models.Model):
    
    _name = 'muk_rest.oauth2'
    _description = "OAuth2 Configuration"

    # ----------------------------------------------------------
    # Fields
    # ----------------------------------------------------------

    oauth_id = fields.Many2one(
        comodel_name='muk_rest.oauth',
        ondelete='cascade',
        string='OAuth',
        delegate=True,  
        required=True,
    )
    
    active = fields.Boolean(
        related='oauth_id.active',
        readonly=False,
        store=True,
        default=True,
    )
    
    state = fields.Selection(
        selection=[
            ('authorization_code', 'Authorization Code'),
            ('implicit', 'Implicit'),
            ('password', 'Password Credentials'),
            ('client_credentials', 'Client Credentials')
        ],
        string="OAuth Type",
        required=True,
        default='authorization_code'
    )
    
    client_id = fields.Char(
        string="Client Key",
        required=True,
        copy=False,
        default=lambda x: common.generate_token()
    )
    
    client_secret = fields.Char(
        string="Client Secret",
        copy=False,
        default=lambda x: common.generate_token()
    )
    
    default_callback_id = fields.Many2one(
        compute='_compute_default_callback_id',
        comodel_name='muk_rest.callback',
        string="Default Callback",
        readonly=True,
        store=True,
    )
    
    user_id = fields.Many2one(
        comodel_name='res.users',
        ondelete='cascade',
        string="User",
    )

    # ----------------------------------------------------------
    # Constraints
    # ----------------------------------------------------------
    
    _sql_constraints = [
        ('client_id_unique', 'UNIQUE (client_id)', 'Client ID must be unique.'),
        ('client_secret_unique', 'UNIQUE (client_secret)', 'Client Secret must be unique.'),
    ]
    
    @api.constrains('state', 'callback_ids')
    def _check_default_callback_id(self):
        for record in self.filtered(lambda rec: rec.state == 'authorization_code'):
            if not record.default_callback_id:
                raise ValidationError(_("Authorization Code needs a default callback."))

    # ----------------------------------------------------------
    # Compute
    # ----------------------------------------------------------
    
    @api.depends('callback_ids', 'callback_ids.sequence')
    def _compute_default_callback_id(self):
        for record in self:
            if len(record.callback_ids) >= 1:
                record.default_callback_id = record.callback_ids[0]
            else:
                record.default_callback_id = False

    # ----------------------------------------------------------
    # ORM
    # ----------------------------------------------------------

    def unlink(self):
        self.mapped('oauth_id').unlink()
        return super(OAuth2, self).unlink()
        