import werkzeug

from odoo import api, http, SUPERUSER_ID
from odoo.exceptions import AccessDenied
from odoo.http import request

from odoo.addons.muk_rest import core
from odoo.addons.muk_rest.tools.http import build_route


class CustomController(http.Controller):
    
    @core.http.rest_route(
        routes=build_route('/custom/<path:endpoint>'),
        rest_access_hidden=True,
        rest_custom=True,
        ensure_db=True
    )
    def custom(self, endpoint, **kw):
        env = api.Environment(request.cr, SUPERUSER_ID, {})
        endpoint = env['muk_rest.endpoint'].search(
            [('endpoint', '=', endpoint)], 
            limit=1
        )
        if endpoint and request.httprequest.method == endpoint.method:
            user = env.ref('base.public_user')
            try:
                user = env['ir.http']._auth_method_rest()
            except (AccessDenied, werkzeug.exceptions.Unauthorized):
                if endpoint.protected:
                    raise
            return endpoint.evaluate(request, user)
        return request.not_found()
