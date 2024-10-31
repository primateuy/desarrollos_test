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


class BinaryTestCase(RestfulCase):
    
    @skip_check_authentication()
    def test_binary(self):
        client = self.authenticate()
        att = self.env["ir.attachment"].search([], limit=1)
        response = client.get(
            self.binary_url, data={"id": att.id, "type": "base64"}
        )
        self.assertTrue(response)
        self.assertTrue(response.json().get("content"))

    @skip_check_authentication()
    def test_binary_file(self):
        client = self.authenticate()
        att = self.env["ir.attachment"].search([], limit=1)
        response = client.get(
            self.binary_url, data={"id": att.id, "type": "file"}
        )
        self.assertTrue(response)
        self.assertTrue(response.content)

    @skip_check_authentication()
    def test_upload_file(self):
        client = self.authenticate()
        tmp_dir = tempfile.mkdtemp()
        filename = os.path.join(tmp_dir, "test.txt")
        try:
            with open(filename, "w") as file:
                file.write("Lorem ipsum!")
            with open(filename, "rb") as file:
                files_01 = {"ufile": file}
                files_02 = {"ufile": file}
                data_01 = {"model": "res.partner", "id": 1}
                data_02 = {"model": "ir.attachment", "id": 1, "field": "datas"}
                response_01 = client.post(self.upload_url, files=files_01, data=data_01)
                response_02 = client.post(self.upload_url, files=files_02, data=data_02)
                self.assertTrue(response_01)
                self.assertTrue(response_02)
        finally:
            shutil.rmtree(tmp_dir)

    @skip_check_authentication()
    def test_upload_files(self):
        client = self.authenticate()
        tmp_dir = tempfile.mkdtemp()
        filename = os.path.join(tmp_dir, "test.txt")
        try:
            with open(filename, "w") as file:
                file.write("Lorem ipsum!")
            with open(filename, "rb") as file:
                files = [("ufile", file), ("ufile", file)]
                data = {"model": "res.partner", "id": 1}
                response = client.post(self.upload_url, files=files, data=data)
                self.assertTrue(response)
        finally:
            shutil.rmtree(tmp_dir)
