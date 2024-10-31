import json
import requests

from urllib import parse

from odoo import api, models, fields
from odoo.addons.muk_rest.tools import common, docs


class ClientGenerator(models.TransientModel):
    
    _name = 'muk_rest.client_generator'
    _description = "Client Generator"

    # ----------------------------------------------------------
    # Selections
    # ----------------------------------------------------------
    
    @api.model
    def _selection_language(self):
        codegen_url = self.get_api_docs_codegen_url()
        language_url = '{}/clients'.format(codegen_url)
        response = requests.get(language_url)
        if response.status_code == 200:
            languages = response.json()
            return [
                (lang, ' '.join(map(lambda l: l.capitalize(), lang.split('-'))))
                for lang in languages
            ]
        return []

    # ----------------------------------------------------------
    # Fields
    # ----------------------------------------------------------

    language = fields.Selection(
        selection='_selection_language',
        string="Language",
        required=True,
    )

    options = fields.Text(
        compute='_compute_options',
        string="Option Values",
        readonly=False,
        store=True,
    )

    send_options = fields.Boolean(
        string="Options"
    )

    # ----------------------------------------------------------
    # Helper
    # ----------------------------------------------------------
    
    def get_api_docs_codegen_url(self):
        codegen_url = self.env['ir.config_parameter'].sudo().get_param(
            'muk_rest.docs_codegen_url', False
        )
        return codegen_url or common.DOCS_CODEGEN_URL

    # ----------------------------------------------------------
    # Compute
    # ----------------------------------------------------------

    @api.depends('send_options', 'language')
    def _compute_options(self):
        codegen_url = '{}/options?version=V3'.format(
            self.get_api_docs_codegen_url()
        )
        for record in self:
            if record.language and record.send_options:
                option_url = '{}&language={}'.format(
                    codegen_url, record.language
                )
                record.options = json.dumps(
                    requests.get(option_url).json(), 
                    sort_keys=True, indent=4
                )
            else:
                record.options = None

    # ----------------------------------------------------------
    # Actions
    # ----------------------------------------------------------

    def action_generate_client(self):
        self.ensure_one()
        generate_url = '/rest/docs/client/{}'.format(
            self.language
        )
        if self.send_options:
            generate_url += '?{}'.format(parse.urlencode({
                'options': self.options
            }))
        return {
            'type': 'ir.actions.act_url',
            'url': generate_url,
            'target': 'new',
        }
