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


class UnlinkTestCase(RestfulCase):
    
    @skip_check_authentication()
    def test_unlink(self):
        client = self.authenticate()
        values = json.dumps({'name': 'Restful Partner'})
        ids = client.post(self.create_url, data={'model': 'res.partner', 'values': values}).json()
        tester = self.env['res.partner'].browse(ids)
        response = client.delete(self.unlink_url, data={'model': 'res.partner', 'ids': ids})
        self.assertTrue(response)
        self.assertFalse(tester.exists())