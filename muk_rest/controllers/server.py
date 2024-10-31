from odoo import http, release, service
from odoo.http import request
from odoo.tools import config

from odoo.addons.muk_rest import core
from odoo.addons.muk_rest.tools.common import VERSION
from odoo.addons.muk_rest.tools.http import build_route


class ServerController(http.Controller):

    #----------------------------------------------------------
    # Components
    #----------------------------------------------------------
    
    @property
    def API_DOCS_COMPONENTS(self):
        return {
            'schemas': {
                'VersionInformation': {
                    'type': 'object',
                    'properties': {
                        'api_version': {
                            'type': 'string',
                        },
                        'server_serie': {
                            'type': 'string',
                        },
                        'server_version': {
                            'type': 'string',
                        },
                        'server_version_info': {
                            'type': 'array',
                            'items': {}
                        },
                    },
                    'description': 'Server version information.'
                }
            }
        }
    
    #----------------------------------------------------------
    # Common
    #----------------------------------------------------------

    @core.http.rest_route(
        routes=build_route('/'), 
        methods=['GET'],
        docs=dict(
            tags=['Server'], 
            summary='Version Information', 
            description='Request version information.',
            responses={
                '200': {
                    'description': 'Version Information', 
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/VersionInformation',
                            },
                            'example': {
                                'api_version': '1',
                                'server_serie': '14.0',
                                'server_version': '14.0',
                                'server_version_info': [14, 0, 0, 'final', 0, '']
                            }
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def version(self, **kw): 
        return request.make_json_response({
            'server_version': release.version,
            'server_version_info': release.version_info,
            'server_serie': release.serie,
            'api_version': VERSION,
        })
    
    @core.http.rest_route(
        routes=build_route('/languages'), 
        methods=['GET'],
        docs=dict(
            tags=['Server'], 
            summary='Languages', 
            description='List of available languages',
            responses={
                '200': {
                    'description': 'Languages', 
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'array',
                                'items': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'string'
                                    },
                                    'minItems': 2,
                                    'maxItems': 2,
                                }
                            },
                            'example': [['sq_AL', 'Albanian'], ['am_ET', 'Amharic']]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def languages(self):
        return request.make_json_response([
            (lang[0], lang[1].split('/')[0].strip()) 
            for lang in service.db.exp_list_lang()
        ])
    
    @core.http.rest_route(
        routes=build_route('/countries'), 
        methods=['GET'],
        docs=dict(
            tags=['Server'], 
            summary='Countries', 
            description='List of available countries',
            responses={
                '200': {
                    'description': 'Countries', 
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'array',
                                'items': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'string'
                                    },
                                    'minItems': 2,
                                    'maxItems': 2,
                                }
                            },
                            'example': [['af', 'Afghanistan'], ['al', 'Albania']]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def countries(self):
        return request.make_json_response(service.db.exp_list_countries())
    
    #----------------------------------------------------------
    # Security
    #----------------------------------------------------------
    
    @core.http.rest_route(
        routes=build_route('/change_master_password'), 
        methods=['POST'],
        disable_logging=True,
        docs=dict(
            tags=['Server'], 
            summary='Change Master Password', 
            description='Change the master password.',
            show=config.get('list_db', True),
            parameter={
                'password_new': {
                    'name': 'password_new',
                    'description': 'New Password',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    }
                },
                'password_old': {
                    'name': 'password_old',
                    'description': 'Old Password',
                    'schema': {
                        'type': 'string'
                    }
                },
            },
            responses={
                '200': {
                    'description': 'Result', 
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'boolean'
                            },
                        }
                    },
                }
            },
            default_responses=['400', '401', '500'],
        )
    )
    @service.db.check_db_management_enabled
    def change_password(self, password_new, password_old='admin' , **kw):
        http.dispatch_rpc('db', 'change_admin_password', [password_old, password_new])
        return request.make_json_response(True)
    