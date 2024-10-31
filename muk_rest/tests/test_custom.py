import os
import json
import urllib
import logging
import requests
import unittest
import requests

from odoo import _, SUPERUSER_ID
from odoo.tests import common

from odoo.addons.muk_rest import validators, tools
from odoo.addons.muk_rest.tests.common import RestfulCase, skip_check_authentication

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

CUSTOM_DOMAIN_URL = 'test_domain'
CUSTOM_ACTION_URL = 'test_action'
CUSTOM_CODE_URL = 'test_code'


class CustomTestCase(RestfulCase):
    
    def setUp(self):
        super(CustomTestCase, self).setUp()
        self.domain_endpoint = self.env['muk_rest.endpoint'].create({
            'name': 'Domain Test',
            'endpoint': CUSTOM_DOMAIN_URL,
            'model_id': self.ref('base.model_res_partner'),
            'method': 'GET',
            'state': 'domain'
        })
        action_vals = {
            'name': 'Action Action',
            'model_id': self.ref('base.model_res_partner'),
            'code': "log('testing')",
            'state': 'code'
        }
        action_model = self.env['ir.actions.server']
        if 'activity_user_type' in action_model._fields :
            action_vals.update({'activity_user_type': 'specific'})
        self.action_endpoint = self.env['muk_rest.endpoint'].create({
            'name': 'Action Test',
            'endpoint': CUSTOM_ACTION_URL,
            'model_id': self.ref('base.model_res_partner'),
            'action_id': action_model.create(action_vals).id,
            'method': 'POST',
            'state': 'action'
        })
        self.code_endpoint = self.env['muk_rest.endpoint'].create({
            'name': 'Code Test',
            'endpoint': CUSTOM_CODE_URL,
            'code': "result = 1",
            'model_id': self.ref('base.model_res_partner'),
            'method': 'POST',
            'state': 'code'
        })
        self.env.flush_all()
    
    @skip_check_authentication()
    def test_domain(self):
        client = self.authenticate()
        response = client.get(self.url_prepare(self.domain_endpoint.route))
        self.assertTrue(response)
        self.assertTrue(response.json())
        
    @skip_check_authentication()
    def test_domain_simple(self):
        client = self.authenticate()
        self.domain_endpoint.write({'domain': '[["id","=",1]]'})
        response = client.get(self.url_prepare(self.domain_endpoint.route))
        self.assertTrue(response)
        self.assertTrue(response.json())
        
    @skip_check_authentication()
    def test_domain_field(self):
        client = self.authenticate()
        self.domain_endpoint.write({'domain_field_ids': [(6, 0, [self.ref('base.field_res_partner__name')])]})
        response = client.get(self.url_prepare(self.domain_endpoint.route))
        self.assertTrue(response)
        self.assertTrue(response.json())
        
    @skip_check_authentication()
    def test_domain_context(self):
        client = self.authenticate()
        self.domain_endpoint.write({'domain': '[["id","=",active_id]]'})
        response = client.get(self.url_prepare(self.domain_endpoint.route), data={'id': 1})
        self.assertTrue(response)
        self.assertTrue(response.json())
        
    @skip_check_authentication()
    def test_domain_demo(self):
        client = self.authenticate("demo", "demo")
        response = client.get(self.url_prepare(self.domain_endpoint.route))
        self.assertTrue(response)
        self.assertTrue(response.json())
        
    @skip_check_authentication()
    def test_action(self):
        client = self.authenticate()
        response = client.post(self.url_prepare(self.action_endpoint.route))
        self.assertTrue(response)
        self.assertTrue(response.json())
        
    @skip_check_authentication()
    def test_code(self):
        client = self.authenticate()
        response = client.post(self.url_prepare(self.code_endpoint.route))
        self.assertTrue(response)
        self.assertTrue(response.json())