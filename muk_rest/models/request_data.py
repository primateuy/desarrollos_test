from odoo import models, api, fields
from odoo.addons.muk_rest.tools import common


class Request(models.Model):
    
    _name = 'muk_rest.request_data'
    _description = "Request"

    # ----------------------------------------------------------
    # Fields
    # ----------------------------------------------------------

    client_key = fields.Char(
        string="Client Key",
        readonly=True,
    )
    
    timestamp = fields.Char(
        string="Timestamp",
        readonly=True,
    )
    
    nonce = fields.Char(
        string="Nonce",
        readonly=True,
    )
    
    token_hash = fields.Char(
        string="Token",
        readonly=True,
    )

    # ----------------------------------------------------------
    # Helper
    # ----------------------------------------------------------
    
    def _check_timestamp_and_nonce(self, client_key, timestamp, nonce, token=None):
        timestamp_and_nonce_domain = [
            ('client_key', '=', client_key), 
            ('timestamp', '=', timestamp), 
            ('nonce', '=', nonce)
        ]
        for record in self.search(timestamp_and_nonce_domain):
            if record.token_hash is None and token is None:
                return False
            elif token and common.KEY_CRYPT_CONTEXT.verify(token, record.token_hash):
                return False
        return self.create({
            'client_key': client_key,
            'timestamp': timestamp,
            'nonce': nonce,
            'token_hash': token and common.hash_token(token) or None
        })

    # ----------------------------------------------------------
    # Autovacuum
    # ----------------------------------------------------------
    
    @api.autovacuum
    def _autovacuum_requests(self):
        limit_date = fields.Datetime.subtract(fields.Datetime.now(), days=1)
        self.search([('create_date', '<', limit_date)]).unlink()
