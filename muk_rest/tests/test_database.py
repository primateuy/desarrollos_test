import io
import os
import logging
import requests
import unittest

from odoo import _, tools
from odoo.tests import common

from odoo.addons.muk_rest import validators, tools
from odoo.addons.muk_rest.tests.common import RestfulCase, skip_check_database
from odoo.addons.muk_rest.tests.common import MASTER_PASSWORD, LOGIN, PASSWORD

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)


class DatabaseTestCase(RestfulCase):
    
    @skip_check_database()
    def test_database_list(self):
        response = self.url_open(self.database_list_url)
        self.assertTrue(response)

    @skip_check_database()
    def test_database_size(self):
        databases = self.url_open(self.database_list_url).json()["databases"]
        response = self.url_open(
            self.database_list_url, data={"database_name": databases[0]}
        )
        self.assertTrue(response)

    @skip_check_database()
    def test_database_create_clone_delete(self):
        response = self.url_open(
            self.database_create_url,
            data={
                "master_password": MASTER_PASSWORD,
                "database_name": "muk_rest_create_db_test",
                "admin_login": LOGIN,
                "admin_password": PASSWORD,
            },
            timeout=300,
        )
        self.assertTrue(response)
        databases = self.url_open(self.database_list_url).json()
        self.assertTrue("muk_rest_create_db_test" in databases["databases"])
        self.assertTrue(
            "muk_rest_create_db_test" not in databases["incompatible_databases"]
        )
        response = self.url_open(
            self.database_duplicate_url,
            data={
                "master_password": MASTER_PASSWORD,
                "database_old": "muk_rest_create_db_test",
                "database_new": "muk_rest_create_clone_test",
            },
            timeout=300,
        )
        self.assertTrue(response)
        databases = self.url_open(self.database_list_url).json()
        self.assertTrue("muk_rest_create_clone_test" in databases["databases"])
        self.assertTrue(
            "muk_rest_create_clone_test" not in databases["incompatible_databases"]
        )
        response = self.url_open(
            self.database_drop_url,
            data={
                "master_password": MASTER_PASSWORD,
                "database_name": "muk_rest_create_db_test",
            },
            timeout=120,
        )
        self.assertTrue(response)
        databases = self.url_open(self.database_list_url).json()
        self.assertTrue("muk_rest_create_db_test" not in databases["databases"])
        self.assertTrue(
            "muk_rest_create_db_test" not in databases["incompatible_databases"]
        )
        response = self.url_open(
            self.database_drop_url,
            data={
                "master_password": MASTER_PASSWORD,
                "database_name": "muk_rest_create_clone_test",
            },
            timeout=120,
        )
        self.assertTrue(response)
        databases = self.url_open(self.database_list_url).json()
        self.assertTrue("muk_rest_create_clone_test" not in databases["databases"])
        self.assertTrue(
            "muk_rest_create_clone_test" not in databases["incompatible_databases"]
        )

    @skip_check_database()
    def test_backup_restore(self):
        response = self.url_open(
            self.database_create_url,
            data={
                "master_password": MASTER_PASSWORD,
                "database_name": "muk_rest_backup_db_test",
                "admin_login": LOGIN,
                "admin_password": PASSWORD,
            },
            timeout=300,
        )
        self.assertTrue(response)
        databases = self.url_open(self.database_list_url).json()
        self.assertTrue("muk_rest_backup_db_test" in databases["databases"])
        self.assertTrue(
            "muk_rest_backup_db_test" not in databases["incompatible_databases"]
        )
        response = self.url_open(
            self.database_backup_url,
            data={
                "master_password": MASTER_PASSWORD,
                "database_name": "muk_rest_backup_db_test",
            },
            timeout=300,
        )
        self.assertTrue(response)
        backup_file = io.BytesIO(response.content)
        self.assertTrue(backup_file)
        response = self.opener.post(
            self.database_restore_url,
            data={
                "master_password": MASTER_PASSWORD,
                "database_name": "muk_rest_restore_db_test",
            },
            files={
                "backup_file": (
                    "backup.zip",
                    backup_file,
                    "application/x-zip-compressed",
                    {"Expires": "0"},
                )
            },
            timeout=300,
        )
        self.assertTrue(response)
        databases = self.url_open(self.database_list_url).json()
        self.assertTrue("muk_rest_restore_db_test" in databases["databases"])
        self.assertTrue(
            "muk_rest_restore_db_test" not in databases["incompatible_databases"]
        )
        response = self.url_open(
            self.database_drop_url,
            data={
                "master_password": MASTER_PASSWORD,
                "database_name": "muk_rest_backup_db_test",
            },
            timeout=120,
        )
        self.assertTrue(response)
        databases = self.url_open(self.database_list_url).json()
        self.assertTrue("muk_rest_backup_db_test" not in databases["databases"])
        self.assertTrue(
            "muk_rest_backup_db_test" not in databases["incompatible_databases"]
        )
        response = self.url_open(
            self.database_drop_url,
            data={
                "master_password": MASTER_PASSWORD,
                "database_name": "muk_rest_restore_db_test",
            },
            timeout=120,
        )
        self.assertTrue(response)
        databases = self.url_open(self.database_list_url).json()
        self.assertTrue("muk_rest_restore_db_test" not in databases["databases"])
        self.assertTrue(
            "muk_rest_restore_db_test" not in databases["incompatible_databases"]
        )
