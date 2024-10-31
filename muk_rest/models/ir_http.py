import json
import threading
import werkzeug
import contextlib

from odoo import api, models, tools, registry, SUPERUSER_ID
from odoo.tools import ustr, ignore, mute_logger
from odoo.http import request, Response

from odoo.addons.muk_rest.core import http
from odoo.addons.muk_rest.tools import common, security, encoder


class IrHttp(models.AbstractModel):
    
    _inherit = 'ir.http'

    # ----------------------------------------------------------
    # Authentication
    # ----------------------------------------------------------

    @classmethod
    def _auth_method_rest(cls):
        env = api.Environment(request.cr, SUPERUSER_ID, {})
        oauth, user = None, None
        
        def update_request(oauth, user):
            request.update_env(user=user.id)
            request.session.update({
                'oauth': oauth and f'{oauth._name},{oauth.id}',
                'context': dict(request.context),
                'login': user.login,
                'uid': user.id,
            })
            return user
        
        def verify_request(verify_request_func):
            try:
                return verify_request_func()
            except Exception:
                return None, None
        
        with env['res.users']._assert_can_auth():
            if common.ACTIVE_BASIC_AUTHENTICATION:
                user, _ = verify_request(http.verify_basic_request)
            if not user and common.ACTIVE_OAUTH1_AUTHENTICATION:
                user, oauth = verify_request(http.verify_oauth1_request)
            if not user and common.ACTIVE_OAUTH2_AUTHENTICATION:
                user, oauth = verify_request(http.verify_oauth2_request)
        
        if not user:
            raise werkzeug.exceptions.Unauthorized()
        return update_request(oauth, user)
            
    #----------------------------------------------------------
    # Logging
    #----------------------------------------------------------

    @classmethod
    def _rest_logging(cls, endpoint, response):
        if (
            tools.config.get('rest_logging', True) and 
            not endpoint.routing.get('disable_logging', False)
        ): 
            with contextlib.suppress(Exception), mute_logger('odoo.sql_db'), registry(
                request.session.db
            ).cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})

                def create_log(env, response):
                    env['muk_rest.logging'].create({
                        'user_id': request.session.uid,
                        'url': request.httprequest.base_url,
                        'ip_address': request.httprequest.remote_addr,
                        'method': request.httprequest.method,
                        'request': '{}\r\n\r\n\r\n{}'.format(
                            '\r\n'.join([
                                '{}: {}'.format(
                                    key, 'authorization' in key.lower() and '***' or value
                                )
                                for key, value in request.httprequest.headers.to_wsgi_list()
                            ]),
                            encoder.encode_request(request)
                        ),
                        'status': getattr(response, 'status_code', None),
                        'response': '{}\r\n{}'.format(
                            ustr(getattr(response, 'headers', '')),
                            encoder.encode_response(response)
                        ),
                    })
                
                if endpoint.routing.get('rest_custom', False):
                    endpoint = env['muk_rest.endpoint'].search(
                        [('endpoint', '=', request.params.get('endpoint'))], 
                        limit=1
                    )
                    if not endpoint or endpoint.logging:
                        create_log(env, response)
                else:
                    create_log(env, response)

    # ----------------------------------------------------------
    # Dispatch
    # ----------------------------------------------------------
    
    @classmethod
    def _dispatch(cls, endpoint):
        if request.session.get('oauth', False):
            oauth_model, oauth_id = request.session['oauth'].split(',')
            oauth = request.env[oauth_model].sudo().browse(int(oauth_id))
            if (
                oauth.security == 'advanced' and
                not oauth.oauth_id._check_security(
                    endpoint.routing, request.params
                )
            ):
                raise werkzeug.exceptions.Unauthorized()
        response = super()._dispatch(endpoint)
        if endpoint.routing.get('type') == common.REST_ROUTING_TYPE:
            cls._rest_logging(endpoint, response)
        return response
    