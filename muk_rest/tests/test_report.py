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


class ReportTestCase(RestfulCase):
        
    @skip_check_authentication()
    def test_reports(self):
        client = self.authenticate()
        response = client.get(self.reports_url)
        self.assertTrue(response)
        self.assertTrue(response.json())
        
    @skip_check_authentication()
    def test_report_single(self):
        client = self.authenticate()
        response = client.get(self.report_url, data={
            'report': 'base.report_irmodulereference', 'ids': json.dumps([1])
        })
        self.assertTrue(response)
        self.assertTrue(response.json().get('content'))
        
    @skip_check_authentication()
    def test_report_multiple(self):
        client = self.authenticate()
        response = client.get(self.report_url, data={
            'report': 'base.report_irmodulereference', 'ids': json.dumps([1, 2])
        })
        self.assertTrue(response)
        self.assertTrue(response.json().get('content'))
        
    @skip_check_authentication()
    def test_report_file(self):
        client = self.authenticate()
        response = client.get(self.report_url, data={
            'report': 'base.report_irmodulereference', 
            'ids': json.dumps([1]), 
            'file_response': True
        })
        self.assertTrue(response)
        self.assertTrue(response.content)
