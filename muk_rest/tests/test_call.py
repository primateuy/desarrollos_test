import os
import json
import urllib
import shutil
import logging
import requests
import unittest
import tempfile

import requests

from odoo import _, SUPERUSER_ID
from odoo.tests import common

from odoo.addons.muk_rest.tests.common import RestfulCase, skip_check_authentication

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)

class CallTestCase(RestfulCase):
    
    @skip_check_authentication()
    def test_call_kwargs(self):
        client = self.authenticate()
        fields_list = ['name']
        tester = self.json_prepare(self.env['res.partner'].default_get(fields_list))
        response = client.post(self.call_url, data={
            'model': 'res.partner', 'method': 'default_get', 'args': json.dumps([fields_list])
        })
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
        
    @skip_check_authentication()
    def test_call_args(self):
        client = self.authenticate()
        fields_list = ['name']
        tester = self.json_prepare(self.env['res.partner'].default_get(fields_list))
        args = json.dumps([fields_list])
        response = client.post(self.call_url, data={'model': 'res.partner', 'method': 'default_get', 'args': args})
        self.assertTrue(response)
        self.assertEqual(response.json(), tester)
        
    @skip_check_authentication()
    def test_call_ids(self):
        client = self.authenticate()
        ids = [1]
        copied_record = self.env['res.partner'].browse(ids).copy()
        tester = self.json_prepare([(copied_record.id, copied_record.display_name)])
        response = client.post(self.call_url, data={'model': 'res.partner', 'method': 'copy', 'ids': json.dumps(ids)})
        self.assertTrue(response)
        self.assertEqual(response.json()[0][1], tester[0][1])
