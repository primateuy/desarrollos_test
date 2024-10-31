from odoo import models, api, fields, _
from odoo.exceptions import AccessError
from odoo.addons.base.models.res_users import check_identity
from odoo.addons.muk_rest.tools import common
    
    
class BearerToken(models.Model):
    
    _name = 'muk_rest.bearer_token'
    _description = "OAuth2 Bearer Token"
    _auto = False

    # ----------------------------------------------------------
    # Setup Database
    # ----------------------------------------------------------
    
    def init(self):
        self.env.cr.execute("""
            CREATE TABLE IF NOT EXISTS {table} (
                id SERIAL PRIMARY KEY,
                access_token VARCHAR NOT NULL,
                refresh_token VARCHAR,
                access_index VARCHAR({index_size}) NOT NULL CHECK (char_length(access_index) = {index_size}),
                refresh_index VARCHAR({index_size}) CHECK (char_length(refresh_index) = {index_size}),
                oauth_id INTEGER NOT NULL REFERENCES muk_rest_oauth2(id),
                user_id INTEGER REFERENCES res_users(id),
                create_date TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'UTC'),
                expiration_date TIMESTAMP WITHOUT TIME ZONE
            );
            CREATE INDEX IF NOT EXISTS {table}_access_index_idx ON {table} (access_index);
            CREATE INDEX IF NOT EXISTS {table}_refresh_index_idx ON {table} (refresh_index);
        """.format(table=self._table, index_size=common.TOKEN_INDEX))

    # ----------------------------------------------------------
    # Fields
    # ----------------------------------------------------------
    
    create_date = fields.Datetime(
        string="Creation Date", 
        readonly=True
    )
    
    expiration_date = fields.Datetime(
        string="Expiration Date",
        readonly=True,
    )
    
    user_id = fields.Many2one(
        comodel_name='res.users',
        ondelete='cascade',
        string="User",
        readonly=True,
    )
    
    oauth_id = fields.Many2one(
        comodel_name='muk_rest.oauth2',
        ondelete='cascade',
        string="Configuration",
        required=True, 
        readonly=True,
    )

    # ----------------------------------------------------------
    # Helper
    # ----------------------------------------------------------
    
    @api.model
    def _check_token(self, token):
        if not token:
            return False
        self.env.cr.execute("""
            SELECT id, access_token FROM {table} 
            WHERE access_index = %s
        """.format(table=self._table), [token[:common.TOKEN_INDEX]])
        for token_id, token_hash in self.env.cr.fetchall():
            if common.KEY_CRYPT_CONTEXT.verify(token, token_hash):
                return self.browse([token_id])
        return False
    
    @api.model
    def _check_refresh(self, token):
        self.env.cr.execute("""
            SELECT id, refresh_token FROM {table} 
            WHERE refresh_index = %s
        """.format(table=self._table), [token[:common.TOKEN_INDEX]])
        for token_id, token_hash in self.env.cr.fetchall():
            if common.KEY_CRYPT_CONTEXT.verify(token, token_hash):
                return self.browse([token_id])
        return False
    
    @api.model
    def _save_bearer_token(self, values):
        fields = ['oauth_id', 'user_id', 'expiration_date', 'access_index', 'access_token']
        insert = [
            values['oauth_id'], 
            values['user_id'], 
            values['expiration_date'],
            values['access_token'][:common.TOKEN_INDEX], 
            common.hash_token(values['access_token'])
        ]
        if values.get('refresh_token', False):
            fields.extend(['refresh_index', 'refresh_token'])
            insert.extend([
                values['refresh_token'][:common.TOKEN_INDEX], 
                common.hash_token(values['refresh_token'])
            ])
        self.env.cr.execute("""
            INSERT INTO {table} ({fields})
            VALUES ({values})
            RETURNING id
        """.format(
            table=self._table, 
            fields=', '.join(fields), 
            values=', '.join(['%s' for _ in range(len(fields))])
        ), insert)
        
    def _remove_bearer_token(self):
        if not (self.env.is_system() or self.user_id == self.env.user):
            raise AccessError(_("You can not remove a Session!"))
        self.sudo().unlink()

    # ----------------------------------------------------------
    # Actions
    # ----------------------------------------------------------
    
    @check_identity
    def action_remove(self):
        self.ensure_one()
        self._remove_bearer_token()
        return {'type': 'ir.actions.act_window_close'}

    # ----------------------------------------------------------
    # Autovacuum
    # ----------------------------------------------------------
    
    @api.autovacuum
    def _autovacuum_token(self):
        params = self.env['ir.config_parameter'].sudo()
        limit_days = int(params.get_param('muk_rest.oauth2_bearer_autovacuum_days', 7))
        limit_date = fields.Datetime.subtract(fields.Datetime.now(), days=limit_days)
        self.search([('expiration_date', '<', limit_date)]).unlink()
