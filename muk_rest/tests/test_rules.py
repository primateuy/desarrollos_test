import os
import urllib
import logging
import requests
import unittest
import requests

from odoo import _, SUPERUSER_ID
from odoo.tests import common

from odoo.addons.muk_rest.tools.common import generate_token
from odoo.addons.muk_rest.tests.common import oauthlib, requests_oauthlib
from odoo.addons.muk_rest.tests.common import skip_check_authentication
from odoo.addons.muk_rest.tests.common import RestfulCase

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class RulesTestCase(RestfulCase):
    
    def setUp(self):
        super(RulesTestCase, self).setUp()
        self.oauth_settings_client_key = generate_token()
        self.oauth_settings_client_secret = generate_token()
        self.oatuh_settings_client = self.env['muk_rest.oauth2'].create({
            'name': "Security Rules Test",
            'client_id': self.oauth_settings_client_key,
            'client_secret': self.oauth_settings_client_secret,
            'state': 'password',
            'security': 'advanced',
            'rule_ids': [(0, 0, {
                'route': '/api/v2/search',
                'sequence': 5,
                'expression_ids': [(0, 0, {
                    'param': 'model',
                    'operation': '*',
                }), (0, 0, {
                    'param': 'model',
                    'operation': '#',
                    'expression': 'res.partner|res.users',
                })]
            }), (0, 0, {
                'route': '/api/v2/.+',
                'sequence': 10,
                'expression_ids': [(0, 0, {
                    'param': 'model',
                    'operation': '=',
                    'expression': 'res.partner',
                })]
            })]
        })
        self.env.flush_all()
        
    @skip_check_authentication()
    def test_oauth_valid(self):
        client = oauthlib.oauth2.LegacyApplicationClient(client_id=self.oauth_settings_client_key)
        oauth = requests_oauthlib.OAuth2Session(client=client)
        oauth.headers.update({self.db_header: self.env.cr.dbname})
        token = oauth.fetch_token(
            token_url=self.oauth2_access_token_url,
            client_id=self.oauth_settings_client_key, 
            client_secret=self.oauth_settings_client_secret,
            username=self.login,
            password=self.password
        )
        self.assertTrue(oauth.get(self.search_url, data={'model': 'res.partner'}))
        
    @skip_check_authentication()
    def test_oauth_invalid(self):
        client = oauthlib.oauth2.LegacyApplicationClient(client_id=self.oauth_settings_client_key)
        oauth = requests_oauthlib.OAuth2Session(client=client)
        oauth.headers.update({self.db_header: self.env.cr.dbname})
        token = oauth.fetch_token(
            token_url=self.oauth2_access_token_url,
            client_id=self.oauth_settings_client_key, 
            client_secret=self.oauth_settings_client_secret,
            username=self.login,
            password=self.password
        )
        self.assertFalse(oauth.get(self.search_url, data={'model': 'res.lang'}))
        
    @skip_check_authentication()
    def test_oauth_generic_rule(self):
        client = oauthlib.oauth2.LegacyApplicationClient(client_id=self.oauth_settings_client_key)
        oauth = requests_oauthlib.OAuth2Session(client=client)
        oauth.headers.update({self.db_header: self.env.cr.dbname})
        token = oauth.fetch_token(
            token_url=self.oauth2_access_token_url,
            client_id=self.oauth_settings_client_key, 
            client_secret=self.oauth_settings_client_secret,
            username=self.login,
            password=self.password
        )
        self.assertTrue(oauth.get(self.xmlid_url, data={'xmlid': 'base.main_company'}))
        self.assertFalse(oauth.get(self.field_names_url, data={'model': 'res.users'}))
        self.assertTrue(oauth.get(self.field_names_url, data={'model': 'res.partner'}))
        self.assertTrue(oauth.get(self.search_url, data={'model': 'res.users'}))
        