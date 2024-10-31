import collections

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, UserError

from odoo.addons.muk_rest import tools, core
from odoo.addons.muk_rest.tools.http import build_route


class SecurityController(http.Controller):
    
    #----------------------------------------------------------
    # Components
    #----------------------------------------------------------
    
    @property
    def API_DOCS_COMPONENTS(self):
        return {
            'schemas': {
                'AccessGroups': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'category_id': {
                                '$ref': '#/components/schemas/RecordTuple',
                            },
                            'comment': {
                                'type': 'string',
                            },
                            'full_name': {
                                'type': 'string',
                            },
                            'id': {
                                'type': 'integer',
                            },
                            'name': {
                                'type': 'string',
                            },
                            'xmlid': {
                                'type': 'string',
                            }
                        },
                    },
                    'description': 'Information about access groups.'
                }
            }
        }

    #----------------------------------------------------------
    # Routes
    #----------------------------------------------------------
    
    @core.http.rest_route(
        routes=build_route([
            '/access/rights',
            '/access/rights/<string:model>',
            '/access/rights/<string:model>/<string:operation>',
        ]), 
        methods=['GET'],
        protected=True,
        docs=dict(
            tags=['Security'], 
            summary='Access Rights', 
            description='Check the access rights for the current user.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'example': 'res.partner',
                },
                'operation': {
                    'name': 'operation',
                    'description': 'Operation',
                    'schema': {
                        'type': 'string'
                    }
                },
            },
            responses={
                '200': {
                    'description': 'Returns True or False', 
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
        ),
    )
    def access_rights(self, model, operation='read', **kw):
        try:
            return request.make_json_response(request.env[model].check_access_rights(operation))
        except (AccessError, UserError):
            pass
        return request.make_json_response(False)

    @core.http.rest_route(
        routes=build_route([
            '/access/rules',
            '/access/rules/<string:model>',
            '/access/rules/<string:model>/<string:operation>',
        ]), 
        methods=['GET'],
        protected=True,
        docs=dict(
            tags=['Security'], 
            summary='Access Rules', 
            description='Check the access rules for the current user.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'example': 'res.partner',
                },
                'ids': {
                    'name': 'ids',
                    'description': 'Record IDs',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs',
                            },
                        },
                    },
                    'example': [],
                },
                'operation': {
                    'name': 'operation',
                    'description': 'Operation',
                    'schema': {
                        'type': 'string'
                    }
                },
            },
            responses={
                '200': {
                    'description': 'Returns True or False', 
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
        ),
    )
    def access_rules(self, model, ids, operation='read', **kw):
        ids = tools.common.parse_ids(ids)
        try:
            return request.make_json_response(
                request.env[model].browse(ids).check_access_rule(operation) is None
            )
        except (AccessError, UserError):
            pass
        return request.make_json_response(False)
    
    @core.http.rest_route(
        routes=build_route([
            '/access/fields',
            '/access/fields/<string:model>',
            '/access/fields/<string:model>/<string:operation>',
        ]), 
        methods=['GET'],
        protected=True,
        docs=dict(
            tags=['Security'], 
            summary='Access Fields', 
            description='Check the access to fields for the current user.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'example': 'res.partner',
                },
                'operation': {
                    'name': 'operation',
                    'description': 'Operation',
                    'schema': {
                        'type': 'string'
                    }
                },
                'fields': {
                    'name': 'fields',
                    'description': 'Fields',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordFields',
                            },
                        }
                    },
                    'example': ['name'],
                },
            },
            responses={
                '200': {
                    'description': 'Returns True or False', 
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
        ),
    )
    def access_fields(self, model, operation='read', **kw):
        try:
            return request.make_json_response(request.env[model].check_field_access_rights(
                operation, request.env[model]._fields
            ))
        except (AccessError, UserError):
            pass
        return request.make_json_response(False)
    
    @core.http.rest_route(
        routes=build_route([
            '/access',
            '/access/<string:model>',
            '/access/<string:model>/<string:operation>',
        ]), 
        methods=['GET'],
        protected=True,
        docs=dict(
            tags=['Security'], 
            summary='Access', 
            description='Check the access for the current user.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'example': 'res.partner',
                },
                'ids': {
                    'name': 'ids',
                    'description': 'Record IDs',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs',
                            },
                        },
                    },
                    'example': [],
                },
                'operation': {
                    'name': 'operation',
                    'description': 'Operation',
                    'schema': {
                        'type': 'string'
                    }
                },
                'fields': {
                    'name': 'fields',
                    'description': 'Fields',
                    'schema': {
                        '$ref': '#/components/schemas/RecordFields',
                    },
                    'example': ['name'],
                },
            },
            responses={
                '200': {
                    'description': 'Returns True or False', 
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
        ),
    )
    def access(self, model, ids, operation='read', **kw):
        ids = tools.common.parse_ids(ids)
        try:
            rights = request.env[model].check_access_rights(operation)
            rules = request.env[model].browse(ids).check_access_rule(operation) is None
            return request.make_json_response(rights and rules)
        except (AccessError, UserError):
            pass
        return request.make_json_response(False)
    
    @core.http.rest_route(
        routes=build_route('/groups'), 
        methods=['GET'],
        protected=True,
        docs=dict(
            tags=['Security'], 
            summary='Access Groups', 
            description='Returns the access groups of the current user.',
            responses={
                '200': {
                    'description': 'Access Groups', 
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/AccessGroups'
                            },
                            'example': [{
                                'category_id': [62, 'Administration'],
                                'comment': False,
                                'full_name': 'Administration / Access Rights',
                                'id': 2,
                                'name': 'Access Rights',
                                'xmlid': 'base.group_erp_manager'
                            }]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def access_groups(self, **kw):
        groups = request.env['res.groups'].sudo().search([
            ('users', '=', request.env.uid)
        ])
        groups_data = groups.read([
            'name', 'category_id', 'full_name', 'comment'
        ])
        xmlids = collections.defaultdict(list)
        model_data = request.env['ir.model.data'].sudo().search_read(
            [('model', '=', 'res.groups'), ('res_id', 'in', groups.ids)], 
            ['module', 'name', 'res_id']
        )
        for rec in model_data:
            xmlids[rec['res_id']].append(
               '{}.{}'.format(rec['module'], rec['name'])
            )
        for rec in groups_data:
            rec['xmlid'] = xmlids.get(rec['id'], [''])[0]
        return request.make_json_response(groups_data)
 
    @core.http.rest_route(
        routes=build_route('/has_group'), 
        methods=['GET'],
        protected=True,
        docs=dict(
            tags=['Security'], 
            summary='Access Group', 
            description='Check if the current user is a member of the group.',
            parameter={
                'group': {
                    'name': 'group',
                    'description': 'XMLID of the Group',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                    'example': 'base.group_user',
                },
            },
            responses={
                '200': {
                    'description': 'Returns True or False', 
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
        ),
    )
    def access_has_group(self, group, **kw):
        return request.make_json_response(request.env.user.has_group(group))
    