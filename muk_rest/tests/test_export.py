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


class ExportTestCase(RestfulCase):
    
    @skip_check_authentication()
    def test_export_single(self):
        client = self.authenticate()
        ids = [1]
        fields = ['name', 'bank_ids/acc_number']
        tester = self.json_prepare(
            self.env['res.partner'].browse(ids).export_data(fields).get('datas', [])
        )
        ids = json.dumps(ids)
        fields = json.dumps(fields)
        response = client.get(self.export_url, data={
            'model': 'res.partner', 'ids': ids, 'fields': fields
        })
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
        
    @skip_check_authentication()
    def test_export_multiple(self):
        client = self.authenticate()
        ids = [1, 2, 3]
        fields = ['name', 'bank_ids/acc_number']
        tester = self.json_prepare(
            self.env['res.partner'].browse(ids).export_data(fields).get('datas', [])
        )
        ids = json.dumps(ids)
        fields = json.dumps(fields)
        response = client.get(self.export_url, data={
            'model': 'res.partner', 'ids': ids, 'fields': fields
        })
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
        