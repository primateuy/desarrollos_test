import os
import json
import logging
import requests
import unittest

from odoo import http, tools, SUPERUSER_ID
from odoo.tests import common

from odoo.addons.muk_rest.tools.encoder import ResponseEncoder
from odoo.addons.muk_rest.tools.common import generate_token
from odoo.addons.muk_rest.tools.http import build_route
from odoo.addons.muk_rest.tests.variables import *

_path = os.path.dirname(os.path.dirname(__file__))
_logger = logging.getLogger(__name__)


def skip_check_authentication():
    return unittest.skipIf(not ACTIVE_AUTHENTICATION, ACTIVE_AUTHENTICATION_TEXT)


def skip_check_database(**kw):
    return unittest.skipIf(DISABLE_DATABASE_TESTS, DISABLE_DATABASE_TEXT)


class RestfulCase(common.HttpCase):
    
    def setUpAuthentication(self):
        self.login = LOGIN
        self.password = PASSWORD
        self.client_key = CLIENT_KEY
        self.client_secret = CLIENT_SECRET
        self.callback_url = CALLBACK_URL
        self.db_param = tools.config.get('rest_db_param', 'db')
        self.db_header = tools.config.get('rest_db_header', 'DATABASE')
        self.test_authentication_url = self.url_prepare(TEST_AUTHENTICATION_URL)
        self.oauth1_request_token_url = self.url_prepare(OAUTH1_REQUEST_TOKEN_URL)
        self.oauth1_authorization_url = self.url_prepare(OAUTH1_AUTHORIZATION_URL)
        self.oauth1_access_token_url = self.url_prepare(OAUTH1_ACCESS_TOKEN_URL)
        self.oauth2_authorization_url = self.url_prepare(OAUTH2_AUTHORIZATION_URL)
        self.oauth2_access_token_url = self.url_prepare(OAUTH2_ACCESS_TOKEN_URL)
        self.oauth2_revoke_url = self.url_prepare(OAUTH2_REVOKE_URL)
        self.test_client_key = generate_token()
        self.test_client_secret = generate_token()
        self.env['muk_rest.oauth2'].create({
            'name': 'OAuth2 Test',
            'client_id': self.test_client_key,
            'client_secret': self.test_client_secret,
            'state': 'password'
        })
        self.origin_transport = os.environ.get('OAUTHLIB_INSECURE_TRANSPORT')
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'OAUTHLIB_INSECURE_TRANSPORT'
        self.env.flush_all()

    def setUpServerUrls(self):
        self.version_url = self.url_prepare(VERSION_URL)
        self.languages_url = self.url_prepare(LANGUAGES_URL)
        self.countries_url = self.url_prepare(COUNTRIES_URL)
        self.database_url = self.url_prepare(DATABASE_URL)
        self.change_master_password_url = self.url_prepare(CHANGE_MASTER_PASSWORD_URL)
        
    def setUpCommonUrls(self):
        self.modules_url = self.url_prepare(MODULES_URL)
        self.xmlid_url = self.url_prepare(XMLID_URL)
        self.user_url = self.url_prepare(USER_URL)
        self.userinfo_url = self.url_prepare(USERINFO_URL)
        self.session_url = self.url_prepare(SESSION_URL)
        
    def setUpBinaryUrls(self):
        self.binary_url = self.url_prepare(BINARY_URL)
        self.upload_url = self.url_prepare(UPLOAD_URL)
        
    def setUpReportUrls(self):
        self.report_url = self.url_prepare(REPORT_URL)
        self.reports_url = self.url_prepare(REPORTS_URL)
        
    def setUpModelUrls(self):
        self.field_names_url = self.url_prepare(FIELD_NAMES_URL)
        self.fields_url = self.url_prepare(FIELDS_URL)
        self.metadata_url = self.url_prepare(METADATA_URL)
        self.call_url = self.url_prepare(CALL_URL)
        self.search_url = self.url_prepare(SEARCH_URL)
        self.name_url = self.url_prepare(NAME_URL)
        self.read_url = self.url_prepare(READ_URL)
        self.search_read_url = self.url_prepare(SEARCH_READ_URL)
        self.read_group_url = self.url_prepare(READ_GROUP_URL)
        self.export_url = self.url_prepare(EXPORT_URL)
        self.extract_url = self.url_prepare(EXTRACT_URL)
        self.create_url = self.url_prepare(CREATE_URL)
        self.write_url = self.url_prepare(WRITE_URL)
        self.write_multi_url = self.url_prepare(WRITE_MULTI_URL)
        self.create_update_url = self.url_prepare(CREATE_UPDATE_URL)
        self.unlink_url = self.url_prepare(UNLINK_URL)
        
    def setUpAccessUrls(self):
        self.access_url = self.url_prepare(ACCESS_URL)
        self.access_rights_url = self.url_prepare(ACCESS_RIGHTS_URL)
        self.access_rules_url = self.url_prepare(ACCESS_RULES_URL)
        self.access_fields_url = self.url_prepare(ACCESS_FIELDS_URL)
        
    def setUpDatabaseUrls(self):
        self.database_list_url = self.url_prepare(DATABASE_LIST)
        self.database_size_url = self.url_prepare(DATABASE_SIZE)
        self.database_create_url = self.url_prepare(DATABASE_CREATE)
        self.database_duplicate_url = self.url_prepare(DATABASE_DUPLICATE)
        self.database_drop_url = self.url_prepare(DATABASE_DROP)
        self.database_backup_url = self.url_prepare(DATABASE_BACKUP)
        self.database_restore_url = self.url_prepare(DATABASE_RESTORE)
          
    def setUp(self):
        super(RestfulCase, self).setUp()
        self.setUpAuthentication()
        self.setUpServerUrls()
        self.setUpCommonUrls()
        self.setUpBinaryUrls()
        self.setUpReportUrls()
        self.setUpModelUrls()
        self.setUpAccessUrls()
        self.setUpDatabaseUrls()
        
    def tearDownAuthentication(self):
        if self.origin_transport:
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = self.origin_transport
        else:
            os.environ.pop('OAUTHLIB_INSECURE_TRANSPORT', None)
                       
    def tearDown(self):
        super(RestfulCase, self).tearDown()
        self.tearDownAuthentication()
    
    def url_prepare(self, url):
        if url.startswith('/'):
            url = "http://{}:{}{}".format(HOST, PORT, url)
        return url
    
    def json_prepare(self, value, encoder=ResponseEncoder):
        return json.loads(json.dumps(value, sort_keys=True, indent=4, cls=encoder))
    
    def authenticate(self, login=LOGIN, password=PASSWORD):
        client = oauthlib.oauth2.LegacyApplicationClient(
            client_id=self.test_client_key
        )
        oauth = requests_oauthlib.OAuth2Session(client=client)
        oauth.headers.update({self.db_header: self.env.cr.dbname})
        token = oauth.fetch_token(
            token_url=self.oauth2_access_token_url,
            client_id=self.test_client_key, 
            client_secret=self.test_client_secret,
            username=login, password=password
        )
        return oauth

    def url_open(self, url, headers=None, *args, **kwargs):
        if headers is None:
            headers = {}
        headers.update({
            self.db_header: self.env.cr.dbname
        })
        return super(RestfulCase, self).url_open(
            url, headers=headers, *args, **kwargs
        )
