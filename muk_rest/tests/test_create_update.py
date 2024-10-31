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


class CreateUpdateTestCase(RestfulCase):
    
    @skip_check_authentication()
    def test_create_update(self):
        client = self.authenticate()
        domain = json.dumps([('id', '=', 2)])
        values = json.dumps({'name': 'Restful Partner'})
        response = client.post(self.create_update_url, data={
            'model': 'res.partner', 'values': values, 'domain': domain,
        })
        tester = self.env['res.partner'].browse(response.json()).name
        self.assertTrue(response)
        self.assertEqual('Restful Partner', tester)
