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

from odoo.addons.muk_rest.tests.common import RestfulCase
from odoo.addons.muk_rest.tests.common import skip_check_database

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)


class ServerTestCase(RestfulCase):
    
    def test_version(self):
        self.assertTrue(self.url_open(self.version_url))
        
    def test_languages(self):
        self.assertTrue(self.url_open(self.languages_url))
        
    def test_countries(self):
        self.assertTrue(self.url_open(self.countries_url))
        
    def test_database(self):
        self.assertTrue(self.url_open(self.database_url))
    
    @skip_check_database()
    def test_change_password(self):
        response = self.url_open(self.change_master_password_url, data={
            'password_old': MASTER_PASSWORD, 'password_new': "new_pw"
        })
        self.assertTrue(response)
        response = requests.post(self.change_master_password_url, data={
            'password_old': "new_pw", 'password_new': MASTER_PASSWORD
        })
        self.assertTrue(response)
        