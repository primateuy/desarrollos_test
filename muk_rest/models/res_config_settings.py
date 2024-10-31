from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    # ----------------------------------------------------------
    # Fields
    # ----------------------------------------------------------

    rest_docs_security_group_id = fields.Many2one(
        comodel_name='res.groups',
        compute='_compute_rest_docs_security_group_id',
        inverse='_inverse_rest_docs_security_group_id',
        string="API Docs Group",
    )

    rest_docs_security_group_xmlid = fields.Char(
        string="API Docs Group XMLID",
        config_parameter='muk_rest.docs_security_group'
    )
    
    rest_oauth2_bearer_expires_in_seconds = fields.Integer(
        string="OAuth 2 Expires In (in Seconds)",
        config_parameter='muk_rest.oauth2_bearer_expires_in_seconds',
        help="If the value is set as -1 the token wont expire at all.",
        default=3600
    )
    
    rest_oauth2_bearer_autovacuum_days = fields.Integer(
        string="OAuth 2 Autovacuum (in Days)",
        config_parameter='muk_rest.oauth2_bearer_autovacuum_days',
        default=7
    )

    # ----------------------------------------------------------
    # Compute
    # ----------------------------------------------------------

    @api.depends('rest_docs_security_group_xmlid')
    def _compute_rest_docs_security_group_id(self):
        for record in self:
            xmlid = record.rest_docs_security_group_xmlid
            group = xmlid and self.env.ref(xmlid, False) or None
            record.rest_docs_security_group_id = group

    # ----------------------------------------------------------
    # Inverse
    # ----------------------------------------------------------

    def _inverse_rest_docs_security_group_id(self):
        records = self.filtered('rest_docs_security_group_id')
        (self - records).write({'rest_docs_security_group_xmlid': False})
        xmlids = records.mapped('rest_docs_security_group_id').get_external_id()
        for record in records: 
            xmlid = xmlids.get(record.rest_docs_security_group_id.id)
            record.write({'rest_docs_security_group_xmlid': xmlid})
