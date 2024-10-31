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


class SearchReadTestCase(RestfulCase):

    @skip_check_authentication()
    def test_search_read(self):
        client = self.authenticate()
        fields = ['name']
        tester = self.json_prepare(self.env['res.partner'].search_read([], fields=fields))
        fields = json.dumps(fields)
        response = client.get(self.search_read_url, data={'model': 'res.partner', 'fields': fields})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
        
    @skip_check_authentication()
    def test_search_read_domain(self):
        client = self.authenticate()
        fields = ['name']
        domain = [['id', '=', 1]]
        tester = self.json_prepare(self.env['res.partner'].search_read(domain, fields=fields))
        fields = json.dumps(fields)
        domain = json.dumps(domain)
        response = client.get(self.search_read_url, data={'model': 'res.partner', 'domain': domain, 'fields': fields})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)

    @skip_check_authentication()
    def test_search_read_domain_context(self):
        client = self.authenticate()
        fields = ['name']
        tester = self.json_prepare(self.env['res.partner'].with_context(bin_size=True).search_read([], fields=fields))
        fields = json.dumps(fields)
        context = json.dumps({'bin_size': True})
        response = client.get(self.search_read_url, data={'model': 'res.partner', 'context': context, 'fields': fields})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
        
    @skip_check_authentication()
    def test_search_read_limit(self):
        client = self.authenticate()
        fields = ['name']
        tester = self.json_prepare(self.env['res.partner'].search_read([], fields=fields, limit=1))
        fields = json.dumps(fields)
        response = client.get(self.search_read_url, data={'model': 'res.partner', 'fields': fields, 'limit': 1})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
        
    @skip_check_authentication()
    def test_search_read_offset(self):
        client = self.authenticate()
        fields = ['name']
        tester = self.json_prepare(self.env['res.partner'].search_read([], fields=fields, offset=1))
        fields = json.dumps(fields)
        response = client.get(self.search_read_url, data={'model': 'res.partner', 'fields': fields, 'offset': 1})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
        
    @skip_check_authentication()
    def test_search_read_order(self):
        client = self.authenticate()
        fields = ['name']
        tester = self.json_prepare(self.env['res.partner'].search_read([], fields=fields, order='name desc'))
        fields = json.dumps(fields)
        response = client.get(self.search_read_url, data={'model': 'res.partner', 'fields': fields, 'order': 'name desc'})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)