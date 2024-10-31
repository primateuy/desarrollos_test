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


class SearchTestCase(RestfulCase):
    
    @skip_check_authentication()
    def test_search(self):
        client = self.authenticate()
        tester = self.json_prepare(self.env['res.partner'].search([]).ids)
        response = client.get(self.search_url, data={'model': 'res.partner'})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
        
    @skip_check_authentication()
    def test_search_count(self):
        client = self.authenticate()
        tester = self.json_prepare(self.env['res.partner'].search([]).ids)
        response = client.get(self.search_url, data={'model': 'res.partner'})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
        
    @skip_check_authentication()
    def test_search_domain_simple(self):
        client = self.authenticate()
        domain = [['id', '=', 1]]
        tester = self.json_prepare(self.env['res.partner'].search(domain).ids)
        domain = json.dumps(domain)
        response = client.get(self.search_url, data={'model': 'res.partner', 'domain': domain})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
    
    @skip_check_authentication()
    def test_search_domain_complex(self):
        client = self.authenticate()
        domain = ['&', ['id', '=', 1], '|', ['category_id', 'child_of', [1]], ['category_id.name', 'ilike', "%"]]
        tester = self.json_prepare(self.env['res.partner'].search(domain).ids)
        domain = json.dumps(domain)
        response = client.get(self.search_url, data={'model': 'res.partner', 'domain': domain})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
    
    @skip_check_authentication()
    def test_search_domain_context(self):
        client = self.authenticate()
        tester = self.json_prepare(self.env['res.partner'].with_context(bin_size=True).search([]).ids)
        context = json.dumps({'bin_size': True})
        response = client.get(self.search_url, data={'model': 'res.partner', 'context': context})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
        
    @skip_check_authentication()
    def test_search_limit(self):
        client = self.authenticate()
        tester = self.json_prepare(self.env['res.partner'].search([], limit=1).ids)
        response = client.get(self.search_url, data={'model': 'res.partner', 'limit': 1})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
        
    @skip_check_authentication()
    def test_search_offset(self):
        client = self.authenticate()
        tester = self.json_prepare(self.env['res.partner'].search([], offset=1).ids)
        response = client.get(self.search_url, data={'model': 'res.partner', 'offset': 1})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
        
    @skip_check_authentication()
    def test_search_order(self):
        client = self.authenticate()
        tester = self.json_prepare(self.env['res.partner'].search([], order='name desc').ids)
        response = client.get(self.search_url, data={'model': 'res.partner', 'order': 'name desc'})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
