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

class ReadGroupTestCase(RestfulCase):
    
    @skip_check_authentication()
    def test_read_group(self):
        client = self.authenticate()
        domain = []
        fields = ['name']
        groupby = ['lang']
        tester = self.json_prepare(self.env['res.partner'].read_group(domain, fields, groupby))
        domain = json.dumps(domain)
        fields = json.dumps(fields)
        groupby = json.dumps(groupby)
        response = client.get(self.read_group_url, data={
            'model': 'res.partner', 'domain': domain, 'fields': fields, 'groupby': groupby})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
        
    @skip_check_authentication()
    def test_read_group_not_lazy(self):
        client = self.authenticate()
        domain = []
        fields = ['name']
        groupby = ['lang']
        tester = self.json_prepare(self.env['res.partner'].read_group(domain, fields, groupby, lazy=False))
        domain = json.dumps(domain)
        fields = json.dumps(fields)
        groupby = json.dumps(groupby)
        response = client.get(self.read_group_url, data={
            'model': 'res.partner', 'domain': domain, 'fields': fields, 'groupby': groupby, 'lazy': False})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
        
    @skip_check_authentication()
    def test_read_group_domain(self):
        client = self.authenticate()
        domain = [['id', '<', 5]]
        fields = ['name']
        groupby = ['lang']
        tester = self.json_prepare(self.env['res.partner'].read_group(domain, fields, groupby))
        domain = json.dumps(domain)
        fields = json.dumps(fields)
        groupby = json.dumps(groupby)
        response = client.get(self.read_group_url, data={
            'model': 'res.partner', 'domain': domain, 'fields': fields, 'groupby': groupby})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
    
    @skip_check_authentication()
    def test_read_group_date(self):
        client = self.authenticate()
        domain = []
        fields = ['name']
        groupby = ['create_date:year']
        tester = self.json_prepare(self.env['res.partner'].with_context(tz='CET').read_group(domain, fields, groupby))
        domain = json.dumps(domain)
        fields = json.dumps(fields)
        groupby = json.dumps(groupby)
        context = json.dumps({'tz': 'CET'})
        response = client.get(self.read_group_url, data={
            'model': 'res.partner', 'domain': domain, 'fields': fields, 'groupby': groupby, 'with_context': context})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
    