from odoo import models, api, fields, _
from odoo.exceptions import AccessError
from odoo.addons.base.models.res_users import check_identity
from odoo.addons.muk_rest.tools import common
    

class AccessToken(models.Model):
    
    _name = 'muk_rest.access_token'
    _description = "OAuth1 Access Token"
    _auto = False

    # ----------------------------------------------------------
    # Setup Database
    # ----------------------------------------------------------
    
    def init(self):
        self.env.cr.execute("""
            CREATE TABLE IF NOT EXISTS {table} (
                id SERIAL PRIMARY KEY,
                resource_owner_key VARCHAR NOT NULL,
                resource_owner_secret VARCHAR NOT NULL,
                index VARCHAR({index_size}) NOT NULL CHECK (char_length(index) = {index_size}),
                oauth_id INTEGER NOT NULL REFERENCES muk_rest_oauth1(id),
                user_id INTEGER NOT NULL REFERENCES res_users(id),
                create_date TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'UTC')
            );
            CREATE INDEX IF NOT EXISTS {table}_index_idx ON {table} (index);
        """.format(table=self._table, index_size=common.TOKEN_INDEX))

    # ----------------------------------------------------------
    # Fields
    # ----------------------------------------------------------
    
    create_date = fields.Datetime(
        string="Creation Date", 
        readonly=True
    )
    
    user_id = fields.Many2one(
        comodel_name='res.users',
        string="User",
        readonly=True,
        ondelete='cascade')
    
    oauth_id = fields.Many2one(
        comodel_name='muk_rest.oauth1',
        string="Configuration",
        required=True,
        readonly=True,
        ondelete='cascade')

    # ----------------------------------------------------------
    # Helper
    # ----------------------------------------------------------
    
    @api.model
    def _check_resource(self, key):
        if not key:
            return False
        self.env.cr.execute("""
            SELECT id, resource_owner_key FROM {table} 
            WHERE index = %s
        """.format(table=self._table), [key[:common.TOKEN_INDEX]])
        for key_id, key_hash in self.env.cr.fetchall():
            if common.KEY_CRYPT_CONTEXT.verify(key, key_hash):
                return self.browse([key_id])
        return False
    
    @api.model
    def _get_secret(self, token_id):
        self.env.cr.execute("""
            SELECT resource_owner_secret FROM {table} 
            WHERE id = %s
        """.format(table=self._table), [token_id])
        return self.env.cr.fetchone()[0]
    
    @api.model
    def _save_resource_owner(self, values):
        fields = ['oauth_id', 'user_id', 'index', 'resource_owner_key', 'resource_owner_secret']
        insert = [
            values['oauth_id'], 
            values['user_id'], 
            values['resource_owner_key'][:common.TOKEN_INDEX], 
            common.hash_token(values['resource_owner_key']),
            values['resource_owner_secret'], 
        ]
        self.env.cr.execute("""
            INSERT INTO {table} ({fields})
            VALUES ({values})
            RETURNING id
        """.format(
            table=self._table, 
            fields=', '.join(fields), 
            values=', '.join(['%s' for _ in range(len(fields))])
        ), insert)
        
    def _remove_resource(self):
        if not (self.env.is_system() or self.user_id == self.env.user):
            raise AccessError(_("You can not remove a Session!"))
        self.sudo().unlink()

    # ----------------------------------------------------------
    # Actions
    # ----------------------------------------------------------
    
    @check_identity
    def action_remove(self):
        self.ensure_one()
        self._remove_resource()
        return {'type': 'ir.actions.act_window_close'}
    