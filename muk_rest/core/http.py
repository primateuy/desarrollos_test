import json
import logging
import werkzeug
import functools

from odoo import http, conf, api, registry, SUPERUSER_ID
from odoo.tools import config, unique
from odoo.http import request, Controller, Response
from odoo.exceptions import AccessDenied

from odoo.addons.muk_rest import validators
from odoo.addons.muk_rest.tools import common
from odoo.addons.muk_rest.tools import security
from odoo.addons.muk_rest.tools.http import clean_query_params
from odoo.addons.muk_rest.tools.encoder import RecordEncoder


def get_controllers(modules=None):
    modules = modules or (
        request.registry._init_modules | 
        set(conf.server_wide_modules)
    )

    def is_valid(cls):
        path = cls.__module__.split('.')
        return (
            path[:2] == ['odoo', 'addons'] and 
            path[2] in modules
        )

    def get_classes(cls):
        result = []
        for subcls in cls.__subclasses__():
            if is_valid(subcls):
                result.extend(get_classes(subcls))
        if not result and is_valid(cls):
            result.append(cls)
        return result
    
    controllers = []
    for module in modules:
        controllers.extend(
            Controller.children_classes.get(module, [])
        )
    for controller in controllers:
        controller_classes = list(unique(get_classes(controller)))
        yield type('Controller', tuple(reversed(controller_classes)), {})()
        

def rest_route(routes=None, docs=None, **kw):
    kw.update({
        'type': common.REST_ROUTING_TYPE, 
        'save_session': False,
        'auth': 'none',
        'csrf': False, 
    })
    
    if (
        not kw.get('cors', False) and 
        config.get('rest_default_cors', False)
    ):
        kw['cors'] = config['rest_default_cors']
    
    if kw.get('protected', False):
        kw['auth'] = common.REST_ROUTING_TYPE
        kw['ensure_db'] = True

    def dec(func):
        @functools.wraps(func)
        @http.route(route=routes, **kw)
        def wrapper(*args, **kwargs):
            if not request.db and kw.get('ensure_db', False):
                message = {
                    'message': "No database could be matched to the request.",
                    'code': 400,
                }
                return request.make_json_response(
                    message, status=400
                )
            result = func(*args, **kwargs)
            if isinstance(result, werkzeug.exceptions.HTTPException):
                message = {
                    'message': result.description,
                    'code': result.code,
                }
                return request.make_json_response(
                    message, status=result.code
                )
            return Response.load(result)
        wrapper.api_docs = (
            docs and docs.copy() or False
        ) 
        return wrapper
    return dec


def check_login_credentials(dbname, login, password):
    model = registry(dbname)['res.users']
    return model.authenticate(dbname, login, password, {
        'interactive': True
    })


def verify_basic_request():
    authorization_header = http.request.httprequest.headers.get('Authorization', '')
    username, password = security.decode_http_basic_authentication(authorization_header)
    env = api.Environment(http.request.cr, SUPERUSER_ID, {})
    user = None
    try:
        user = env['res.users'].browse(int(username))
        user.with_user(user)._check_credentials(
            password, {'interactive': False}
            )
    except:
        user = env['res.users'].search([('login', '=', username)], limit=1)
        user.with_user(user)._check_credentials(password, {'interactive': False})
    return user, False
    

def verify_oauth1_request():
    valid, request = validators.oauth1_provider.validate_protected_resource_request(
        uri=clean_query_params(http.request.httprequest.url, clean_db=True),
        http_method=http.request.httprequest.method,
        body=http.request.httprequest.form,
        headers=dict(http.request.httprequest.headers.to_wsgi_list()),
        realms=list()
    )
    access_token = request and request.access_token or None
    if not valid or not (access_token and access_token.user_id):
        raise AccessDenied()
    return access_token.user_id, access_token.oauth_id


def verify_oauth2_request():
    valid, request = validators.oauth2_provider.verify_request(
        uri=clean_query_params(http.request.httprequest.url, clean_db=True),
        http_method=http.request.httprequest.method,
        body=http.request.httprequest.form,
        headers=dict(http.request.httprequest.headers.to_wsgi_list()),
        scopes=list()
    )
    if not valid or not (request and request.access_token):
        raise AccessDenied()
    access_token = request.access_token
    oauth = access_token.oauth_id
    user = access_token.user_id
    if (
        not user and oauth._name == 'muk_rest.oauth2' and
        oauth.state == 'client_credentials' and oauth.user_id
    ):
        user = request.access_token.oauth_id.user_id
    if not user:
        raise AccessDenied()
    return user, access_token.oauth_id


@common.monkey_patch(http.Request)
def _get_session_and_dbname(self):
    if common.BASE_URL in self.httprequest.base_url:
        host = self.httprequest.environ['HTTP_HOST']
        db_param = config.get('rest_db_param', 'db')
        db_header = config.get('rest_db_header', 'DATABASE')

        session = http.root.session_store.new()
        session.update(http.get_default_session())
        session.context['lang'] = self.default_lang()
        
        database = self.httprequest.args.get(
            db_param, self.httprequest.form.get(
                db_param, self.httprequest.environ.get(
                    'HTTP_{}'.format(db_header.upper().replace('-', '_')), 
                )
            )
        )
        database = database and database.strip()
        if not database:
            databases = http.db_list(force=True, host=host)
            if len(databases) == 1:
                database = databases[0]
        
        if database and database in http.db_filter(
            [database], host=host
        ):
            session.db = database
            return session, session.db
        return session, None
    return _get_session_and_dbname.super(self)


@common.monkey_patch(http.Request)
def make_json_response(self, data, headers=None, cookies=None, status=200):
    if self.dispatcher and self.dispatcher.routing_type == common.REST_ROUTING_TYPE:
        headers = werkzeug.datastructures.Headers(headers)
        if common.CONTENT_TYPE_HEADER_KEY not in headers:
            headers[common.CONTENT_TYPE_HEADER_KEY] = (
                common.CONTENT_TYPE_HEADER_VALUE
            )
        data = json.dumps(
            data,
            ensure_ascii=False, 
            sort_keys=True, 
            indent=4, 
            cls=RecordEncoder
        )
        headers['Content-Length'] = len(data)
        return self.make_response(
            data, headers.to_wsgi_list(), cookies, status
        )
    return make_json_response.super(
        self, data, headers=headers, cookies=cookies, status=status
    )


class RESTDispatcher(http.Dispatcher):
    routing_type = common.REST_ROUTING_TYPE

    @classmethod
    def is_compatible_with(cls, request):
        return True

    def dispatch(self, endpoint, args):
        self.request.params = dict(self.request.get_http_params(), **args)
        if (
            self.request.httprequest.mimetype in common.JSON_MIMETYPE and
            self.request.httprequest.method in ('POST', 'PUT')
        ):
            data = self.request.httprequest.get_data().decode(
                self.request.httprequest.charset
            )
            body = common.parse_value(data, {})
            if not isinstance(body, dict):
                body = {'data': body}
            self.request.params.update(body)

        self.request.update_context(**common.parse_value(
            self.request.params.pop('with_context', False), {}
        ))
        if self.request.params.get('with_company', False):
            with_company_id = int(
                self.request.params.pop('with_company')
            )
            allowed_company_ids = self.request.context.get(
                'allowed_company_ids', []
            )
            if with_company_id in allowed_company_ids:
                allowed_company_ids.remove(with_company_id)
            allowed_company_ids.insert(0, with_company_id)
            self.request.update_context(
                allowed_company_ids=allowed_company_ids
            )

        if self.request.db:
            result = self.request.registry['ir.http']._dispatch(endpoint)
        else:
            result = endpoint(**self.request.params)
        return result

    def handle_error(self, exc):
        message = common.parse_exception(exc)
        return request.make_json_response(
            message, status=message.get('code', 500)
        )
