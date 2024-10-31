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


class SecurityTestCase(RestfulCase):
    
    @skip_check_authentication()
    def test_access_rights(self):
        client = self.authenticate()
        response = client.get(self.access_rights_url, data={'model': 'res.partner'})
        self.assertTrue(response)
        self.assertTrue(response.json())
        
    @skip_check_authentication()
    def test_access_rights(self):
        client = self.authenticate()
        response = client.get(self.access_rules_url, data={'model': 'res.partner', 'ids': json.dumps([1, 2])})
        self.assertTrue(response)
        self.assertTrue(response.json())
        
    @skip_check_authentication()
    def test_access_fields(self):
        client = self.authenticate()
        response = client.get(self.access_fields_url, data={'model': 'res.partner'})
        self.assertTrue(response)
        self.assertTrue(response.json())
        
    @skip_check_authentication()
    def test_access(self):
        client = self.authenticate()
        response = client.get(self.access_url, data={'model': 'res.partner', 'ids': json.dumps([1, 2])})
        self.assertTrue(response)
        self.assertTrue(response.json())