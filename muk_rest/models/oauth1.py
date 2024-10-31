from odoo import models, api, fields, _
from odoo.exceptions import ValidationError

from odoo.addons.muk_rest.tools import common


class OAuth1(models.Model):
    
    _name = 'muk_rest.oauth1'
    _description = "OAuth1 Configuration"

    # ----------------------------------------------------------
    # Fields
    # ----------------------------------------------------------

    oauth_id = fields.Many2one(
        comodel_name='muk_rest.oauth',
        string='OAuth',
        delegate=True,  
        required=True,
        ondelete='cascade')

    active = fields.Boolean(
        related='oauth_id.active',
        readonly=False,
        store=True,
        default=True,
    )
    
    consumer_key = fields.Char(
        string="Consumer Key",
        required=True,
        copy=False,
        default=lambda x: common.generate_token()
    )
    
    consumer_secret = fields.Char(
        string="Consumer Secret",
        required=True,
        copy=False,
        default=lambda x: common.generate_token()
    )

    # ----------------------------------------------------------
    # Constraints
    # ----------------------------------------------------------
    
    _sql_constraints = [
        ('consumer_key_unique', 'UNIQUE (consumer_key)', 'Consumer Key must be unique.'),
        ('consumer_secret_unique', 'UNIQUE (consumer_secret)', 'Consumer Secret must be unique.'),
    ]
    
    @api.constrains('consumer_key')
    def check_consumer_key(self):
        for record in self:
            if not (20 < len(record.consumer_key) < 50):
                raise ValidationError(_("The consumer key must be between 20 and 50 characters long."))
            
    @api.constrains('consumer_secret')
    def check_consumer_secret(self):
        for record in self:
            if not (20 < len(record.consumer_secret) < 50):
                raise ValidationError(_("The consumer secret must be between 20 and 50 characters long."))

    # ----------------------------------------------------------
    # ORM
    # ----------------------------------------------------------

    def unlink(self):
        self.mapped('oauth_id').unlink()
        return super(OAuth1, self).unlink()
