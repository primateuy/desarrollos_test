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


class ExtractTestCase(RestfulCase):
    
    @skip_check_authentication()
    def test_extract_single(self):
        client = self.authenticate()
        ids = [1]
        fields = ['name', 'bank_ids/acc_number']
        tester = self.json_prepare(
            self.env['res.partner'].browse(ids).rest_extract_data(fields)
        )
        ids = json.dumps(ids)
        fields = json.dumps(fields)
        response = client.get(self.extract_url, data={
            'model': 'res.partner', 'ids': ids, 'fields': fields
        })
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
        
    @skip_check_authentication()
    def test_extract_multiple(self):
        client = self.authenticate()
        ids = [1, 2, 3]
        fields = ['name', 'bank_ids/acc_number']
        tester = self.json_prepare(
            self.env['res.partner'].browse(ids).rest_extract_data(fields)
        )
        ids = json.dumps(ids)
        fields = json.dumps(fields)
        response = client.get(self.extract_url, data={
            'model': 'res.partner', 'ids': ids, 'fields': fields
        })
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
        