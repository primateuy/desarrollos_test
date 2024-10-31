from odoo import api, tools, fields, models


class RESTLogging(models.Model):
    
    _name = 'muk_rest.logging'
    _description = 'REST Logs'
    _order = 'create_date desc'
    _rec_name = 'url'

    # ----------------------------------------------------------
    # Fields
    # ----------------------------------------------------------

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User',
    )

    ip_address = fields.Char(
        string="IP Address"
    )

    url = fields.Char(
        string="URL"
    )

    method = fields.Char(
        string="Method"
    )

    request = fields.Text(
        string="Request"
    )

    status = fields.Char(
        string="Status"
    )
    
    response = fields.Text(
        string="Response"
    )

    # ----------------------------------------------------------
    # Autovacuum
    # ----------------------------------------------------------
    
    @api.autovacuum
    def _autovacuum_logs(self):
        limit_days = int(tools.config.get('rest_logging_autovacuum', 30))
        limit_date = fields.Datetime.subtract(fields.Datetime.now(), days=limit_days)
        self.search([('create_date', '<', limit_date)]).unlink()
        