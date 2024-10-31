from odoo import _, models, api, fields
from odoo.addons.muk_rest.tools import common

class AuthorizationCode(models.Model):
    
    _name = 'muk_rest.authorization_code'
    _description = "OAuth2 Authorization Code"
    _auto = False
    
    #----------------------------------------------------------
    # Setup Database
    #----------------------------------------------------------
    
    def init(self):
        self.env.cr.execute("""
            CREATE TABLE IF NOT EXISTS {table} (
                id SERIAL PRIMARY KEY,
                state VARCHAR,
                callback VARCHAR,
                code VARCHAR NOT NULL,
                index VARCHAR({index_size}) NOT NULL CHECK (char_length(index) = {index_size}),
                oauth_id INTEGER NOT NULL REFERENCES muk_rest_oauth2(id),
                user_id INTEGER NOT NULL REFERENCES res_users(id),
                create_date TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'UTC')
            );
            CREATE INDEX IF NOT EXISTS {table}_index_idx ON {table} (index);
        """.format(table=self._table, index_size=common.TOKEN_INDEX))

    #----------------------------------------------------------
    # Fields
    #----------------------------------------------------------
    
    create_date = fields.Datetime(
        string="Creation Date", 
        readonly=True
    )

    callback = fields.Char(
        string="Callback",
        readonly=True
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
    
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------
    
    @api.model
    def _check_code(self, code, state=None):
        if not code:
            return False
        self.env.cr.execute(
            "SELECT id, code FROM {table} WHERE index = %s {where_state}".format(
                table=self._table, where_state=(state and 'AND (state IS NULL OR state = %s)' or '')
            ), 
            [code[:common.TOKEN_INDEX]], state
        )
        for code_id, code_hash in self.env.cr.fetchall():
            if common.KEY_CRYPT_CONTEXT.verify(code, code_hash):
                return self.browse([code_id])
        return False

    @api.model
    def _save_authorization_code(self, values):
        fields = ['oauth_id', 'user_id', 'callback', 'index', 'code']
        insert = [
            values['oauth_id'], 
            values['user_id'], 
            values['callback'],
            values['code'][:common.TOKEN_INDEX], 
            common.hash_token(values['code'])
        ]
        if values.get('state', False):
            fields.append('state')
            insert.append(values['state'])
        self.env.cr.execute("""
            INSERT INTO {table} ({fields})
            VALUES ({values})
            RETURNING id
        """.format(
            table=self._table, 
            fields=', '.join(fields), 
            values=', '.join(['%s' for _ in range(len(fields))])
        ), insert)
    
    #----------------------------------------------------------
    # Autovacuum
    #----------------------------------------------------------
    
    @api.autovacuum
    def _autovacuum_code(self):
        limit_date = fields.Datetime.subtract(fields.Datetime.now(), days=7)
        self.search([('create_date', '<', limit_date)]).unlink()
