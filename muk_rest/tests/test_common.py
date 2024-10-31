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


class CommonTestCase(RestfulCase):
    
    @skip_check_authentication()
    def test_modules(self):
        client = self.authenticate()
        self.assertTrue(client.get(self.modules_url))
    
    @skip_check_authentication()
    def test_xmlid(self):
        client = self.authenticate()
        tester = self.env.ref('base.group_user')
        response = client.get(self.xmlid_url, data={'xmlid': 'base.group_user'})
        self.assertTrue(response)
    
    @skip_check_authentication()
    def test_user(self):
        client = self.authenticate()
        response = client.get(self.user_url)
        self.assertTrue(response)
        self.assertTrue(response.json().get('uid'))
    
    @skip_check_authentication()
    def test_userinfo(self):
        client = self.authenticate()
        response = client.get(self.userinfo_url)
        self.assertTrue(response)
        self.assertTrue(response.json().get('name'))
    
    @skip_check_authentication()
    def test_session(self):
        client = self.authenticate()
        response = client.get(self.session_url)
        self.assertTrue(response)
        self.assertTrue(response.json().get('name'))
