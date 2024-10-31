import werkzeug

from odoo import http
from odoo.http import request
from odoo.models import check_method_name
from odoo.tools import misc, osutil

from odoo.addons.muk_rest import tools, core
from odoo.addons.muk_rest.tools.http import build_route
from odoo.addons.web.controllers.export import CSVExport, ExcelExport


class ModelController(http.Controller):
    
    #----------------------------------------------------------
    # Components
    #----------------------------------------------------------
    
    @property
    def API_DOCS_COMPONENTS(self):
        return {
            'schemas': {
                'ReadGroupResult': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            '__domain': {
                                '$ref': '#/components/schemas/Domain',
                            }
                        },
                        'additionalProperties': True,
                    },
                    'description': 'A list of grouped record information.'
                },
                'DataFields': {
                    'type': 'array',
                    'items': {
                        'type': 'string'
                    },
                    'description': (
                        'A list of field names. The field names can be separated '
                        'with a "/" to access fields of a linked model.'
                    )
                },
                'ExportData': {
                    'type': 'array',
                    'items': {
                        'type': 'array',
                    },
                    'description': 'A list of the exported data.'
                },
                'ExtractData': {
                    'type': 'object',
                    'description': 'A map of field names and their corresponding values.'
                },
                'MultiWriteValues': {
                    'type': 'array',
                    'items': {
                        'type': 'array',
                        'items': {
                            'anyOf': [
                                {'$ref': '#/components/schemas/RecordIDs'},
                                {'$ref': '#/components/schemas/RecordValues'},
                            ]
                        },
                        'minItems': 2,
                        'maxItems': 2,
                    },
                    'description': 'A list write commands.'
                }
            }
        }
  
    #----------------------------------------------------------
    # Generic Method
    #----------------------------------------------------------
     
    @core.http.rest_route(
        routes=build_route([
            '/call',
            '/call/<string:model>',
            '/call/<string:model>/<string:method>',
        ]), 
        methods=['POST'],
        protected=True,
        docs=dict(
            tags=['Model'], 
            summary='Call', 
            description='Generic method call.',
            parameter={
                'model': {
                    'name': 'model',
                    'description': 'Model',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
                },
                'method': {
                    'name': 'method',
                    'description': 'Method',
                    'required': True,
                    'schema': {
                        'type': 'string'
                    },
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
                'args': {
                    'name': 'args',
                    'description': 'Positional Arguments',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'array',
                                'items': {}
                            },
                        },
                    },
                    'example': [],
                },
                'kwargs': {
                    'name': 'kwargs',
                    'description': 'Keyword Arguments',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object'
                            },
                        },
                    },
                    'example': {},
                },
            },
            default_responses=['200', '400', '401', '500'],
        ),
    )
    def call(self, model, method, ids=None, args=None, kwargs=None, **kw):
        check_method_name(method)
        args = tools.common.parse_value(args, []) 
        kwargs = tools.common.parse_value(kwargs, {})
        records = request.env[model].browse(
            tools.common.parse_ids(ids)
        )
        return request.make_json_response(
            getattr(records, method)(*args, **kwargs)
        )

    #----------------------------------------------------------
    # Search / Read
    #----------------------------------------------------------

    @core.http.rest_route(
        routes=build_route([
            '/search',
            '/search/<string:model>',
            '/search/<string:model>/<string:order>',
            '/search/<string:model>/<int:limit>/<string:order>',
            '/search/<string:model>/<int:limit>/<int:offset>/<string:order>'
        ]), 
        methods=['GET', 'POST'],
        protected=True,
        docs=dict(
            tags=['Model'], 
            summary='Search', 
            description='Search for matching records',
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
                'domain': {
                    'name': 'domain',
                    'description': 'Search Domain',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/Domain',
                            },
                        }
                    },
                    'example': ['|', ('is_company', '=', True), ('parent_id', '=', False)],
                },
                'count': {
                    'name': 'count',
                    'description': 'Count',
                    'schema': {
                        'type': 'boolean'
                    },
                },
                'limit': {
                    'name': 'limit',
                    'description': 'Limit',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'offset': {
                    'name': 'offset',
                    'description': 'Offset',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'order': {
                    'name': 'order',
                    'description': 'Order',
                    'schema': {
                        'type': 'string'
                    },
                },
            },
            responses={
                '200': {
                    'description': 'Records IDs', 
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs'
                            },
                            'example': [1, 2, 3]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def search(
        self, 
        model, 
        domain=None, 
        count=False, 
        limit=None, 
        offset=0, 
        order=None, 
        **kw
    ):
        domain = tools.common.parse_domain(domain)
        count = count and misc.str2bool(count) or None
        limit = limit and int(limit) or None
        offset = offset and int(offset) or None
        model = request.env[model].with_context(prefetch_fields=False)
        if count:
            record_count = model.search_count(domain)
            return request.make_json_response(record_count)

        result = model.search(domain, offset=offset, limit=limit, order=order)
        return request.make_json_response(result.ids)
            
    @core.http.rest_route(
        routes=build_route([
            '/name',
            '/name/<string:model>',
        ]), 
        methods=['GET', 'POST'],
        protected=True,
        docs=dict(
            tags=['Model'], 
            summary='Names', 
            description='Get the record names.',
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
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs',
                            },
                        },
                    },
                    'example': [1, 2, 3],
                },
            },
            responses={
                '200': {
                    'description': 'List of ID and Name Tupels', 
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordTuples'
                            },
                            'example': [[1, 'YourCompany']]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def name(self, model, ids, **kw):
        records = request.env[model].browse(tools.common.parse_ids(ids))
        return request.make_json_response(
            [(record.id, record.display_name) for record in records]
        )

    @core.http.rest_route(
        routes=build_route([
            '/read',
            '/read/<string:model>',
        ]), 
        methods=['GET', 'POST'],
        protected=True,
        docs=dict(
            tags=['Model'], 
            summary='Read', 
            description='Read the given records.',
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
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs',
                            },
                        },
                    },
                    'example': [1, 2, 3],
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
                    'description': 'List of ID and name tupels', 
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordData'
                            },
                            'example': [{
                                'active': True,
                                'id': 14,
                                'name': 'Azure Interior'
                            }]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def read(self, model, ids, fields=None, **kw):
        return request.make_json_response(
            request.env[model].browse(
                tools.common.parse_ids(ids)
            ).read(
                tools.common.parse_value(fields)
            )
        )

    @core.http.rest_route(
        routes=build_route([
            '/search_read',
            '/search_read/<string:model>',
            '/search_read/<string:model>/<string:order>',
            '/search_read/<string:model>/<int:limit>/<string:order>',
            '/search_read/<string:model>/<int:limit>/<int:offset>/<string:order>'
        ]), 
        methods=['GET', 'POST'],
        protected=True,
        docs=dict(
            tags=['Model'], 
            summary='Search Read', 
            description='Search for matching records.',
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
                'domain': {
                    'name': 'domain',
                    'description': 'Search Domain',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/Domain',
                            },
                        }
                    },
                    'example': ['|', ('is_company', '=', True), ('parent_id', '=', False)],
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
                'limit': {
                    'name': 'limit',
                    'description': 'Limit',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'offset': {
                    'name': 'offset',
                    'description': 'Offset',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'order': {
                    'name': 'order',
                    'description': 'Order',
                    'schema': {
                        'type': 'string'
                    },
                },
            },
            responses={
                '200': {
                    'description': 'Records', 
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordData'
                            },
                            'example': [{
                                'active': True,
                                'id': 14,
                                'name': 'Azure Interior'
                            }]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def search_read(
        self, 
        model, 
        domain=None, 
        fields=None, 
        limit=None, 
        offset=0, 
        order=None, 
        **kw
    ):
        domain = tools.common.parse_domain(domain)
        fields = tools.common.parse_value(fields)
        limit = limit and int(limit) or None
        offset = offset and int(offset) or None
        return request.make_json_response(request.env[model].search_read(
            domain, fields=fields, offset=offset, limit=limit, order=order
        ))

    @core.http.rest_route(
        routes=build_route([
            '/read_group',
            '/read_group/<string:model>',
            '/read_group/<string:model>/<string:orderby>',
            '/read_group/<string:model>/<int:limit>/<string:orderby>',
            '/read_group/<string:model>/<int:limit>/<int:offset>/<string:orderby>'
        ]), 
        methods=['GET', 'POST'],
        protected=True,
        docs=dict(
            tags=['Model'], 
            summary='Read Group', 
            description='Search for matching records.',
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
                'domain': {
                    'name': 'domain',
                    'required': True,
                    'description': 'Search Domain',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/Domain',
                            },
                        }
                    },
                    'example': ['|', ('is_company', '=', True), ('parent_id', '=', False)],
                },
                'fields': {
                    'name': 'fields',
                    'description': 'Fields',
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordFields',
                            },
                        }
                    },
                    'example': ['name', 'parent_id'],
                },
                'groupby': {
                    'name': 'groupby',
                    'description': 'GroupBy',
                    'required': True,
                    'schema': {
                        'type': 'array',
                        'items': {
                            'type': 'string',
                        }
                    },
                    'example': ['parent_id'],
                },
                'limit': {
                    'name': 'limit',
                    'description': 'Limit',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'offset': {
                    'name': 'offset',
                    'description': 'Offset',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'orderby': {
                    'name': 'orderby',
                    'description': 'Order',
                    'schema': {
                        'type': 'string'
                    },
                },
                'lazy': {
                    'name': 'lazy',
                    'description': 'Lazy Loading',
                    'schema': {
                        'type': 'boolean'
                    },
                },
            },
            responses={
                '200': {
                    'description': 'Records', 
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/ReadGroupResult',
                            },
                            'example': [{
                                '__domain': [
                                    '&', ['parent_id', '=', False],
                                    '|', ['is_company', '=', True],
                                    ['parent_id', '=', False]
                                ],
                                'parent_id': False,
                                'parent_id_count': 12
                            }]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def read_group(
        self, 
        model, 
        domain, 
        fields, 
        groupby, 
        offset=0, 
        limit=None, 
        orderby=False, 
        lazy=True, 
        **kw
    ):
        domain = tools.common.parse_domain(domain)
        fields = tools.common.parse_value(fields)
        groupby = tools.common.parse_value(groupby, [])
        limit = limit and int(limit) or None
        offset = offset and int(offset) or None
        lazy = misc.str2bool(lazy)
        return request.make_json_response(request.env[model].read_group(
            domain, fields, groupby=groupby, offset=offset, 
            limit=limit, orderby=orderby, lazy=lazy
        ))

    @core.http.rest_route(
        routes=build_route([
            '/export',
            '/export/<string:model>',
            '/export/<string:model>/<string:type>',
        ]), 
        methods=['GET', 'POST'],
        protected=True,
        docs=dict(
            tags=['Model'], 
            summary='Export', 
            description='Export the given records.',
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
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs',
                            },
                        },
                    },
                    'example': [1, 3],
                },
                'fields': {
                    'name': 'fields',
                    'description': 'Fields',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/DataFields',
                            },
                        }
                    },
                    'example': ['name', 'bank_ids/acc_number'],
                },
                'type': {
                    'name': 'type',
                    'description': 'Return the Response as a CSV, Excel or Array',
                    'schema': {
                        'type': 'string',
                        'enum': ['csv', 'xlsx', 'array'],
                    },
                    'example': 'array',
                },
            },
            responses={
                '200': {
                    'description': 'Export Data', 
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/ExportData'
                            },
                            'example': [
                                ['YourCompany', ''],
                                ['Mitchell Admin', ''],
                            ],
                        },
                        'application/octet-stream': {
                            'schema': {
                                'type': 'string',
                                'format': 'binary'
                            }
                        }
                        
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def export(self, model, ids, fields=None, type='array', **kw):
        records = request.env[model].browse(
            tools.common.parse_ids(ids)
        )
        field_names = tools.common.parse_value(fields)
        data  = records.export_data(field_names).get('datas', [])
        if type in ('csv', 'xlsx'):
            exporter = CSVExport() if type == 'csv' else ExcelExport()
            disposition = http.content_disposition(
                osutil.clean_filename(f'{records._table}{exporter.extension}')
            )
            content = exporter.from_data(field_names, data)
            return request.make_response(
                content, 
                headers=[
                    ('Content-Length', len(content)),
                    ('Content-Type', exporter.content_type),
                    ('Content-Disposition', disposition),
                ],
            )
        return request.make_json_response(data)

    @core.http.rest_route(
        routes=build_route([
            '/extract',
            '/extract/<string:model>',
        ]), 
        methods=['GET', 'POST'],
        protected=True,
        docs=dict(
            tags=['Model'], 
            summary='Extract', 
            description='Extract the given records.',
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
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs',
                            },
                        },
                    },
                    'example': [1, 2],
                },
                'fields': {
                    'name': 'fields',
                    'description': 'Fields',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/DataFields',
                            },
                        }
                    },
                    'example': ['name', 'bank_ids/acc_number'],
                },
                'metadata': {
                    'name': 'metadata',
                    'description': 'Show Metadata',
                    'schema': {
                        'type': 'boolean'
                    },
                },
            },
            responses={
                '200': {
                    'description': 'Extract Data', 
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/ExtractData'
                            },
                            'example': [
                              {'bank_ids': [], 'id': 1, 'name': 'YourCompany'},
                              {'bank_ids': [], 'id': 2, 'name': 'OdooBot'}
                            ],
                        },
                        
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def extract(self, model, ids, fields=None, metadata=False, **kw):
        records = request.env[model].browse(
            tools.common.parse_ids(ids)
        )
        return request.make_json_response(
            records.rest_extract_data(
                tools.common.parse_value(fields),
                metadata=metadata
            )
        )

    @core.http.rest_route(
        routes=build_route([
            '/search_extract',
            '/search_extract/<string:model>',
            '/search_extract/<string:model>/<string:order>',
            '/search_extract/<string:model>/<int:limit>/<string:order>',
            '/search_extract/<string:model>/<int:limit>/<int:offset>/<string:order>'
        ]), 
        methods=['GET', 'POST'],
        protected=True,
        docs=dict(
            tags=['Model'], 
            summary='Search Extract', 
            description='Search the given domain and extract the fields.',
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
                'domain': {
                    'name': 'domain',
                    'description': 'Search Domain',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/Domain',
                            },
                        }
                    },
                    'example': ['|', ('is_company', '=', True), ('parent_id', '=', False)],
                },
                'fields': {
                    'name': 'fields',
                    'description': 'Fields',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/DataFields',
                            },
                        }
                    },
                    'example': ['name', 'bank_ids/acc_number'],
                },
                'limit': {
                    'name': 'limit',
                    'description': 'Limit',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'offset': {
                    'name': 'offset',
                    'description': 'Offset',
                    'schema': {
                        'type': 'integer'
                    },
                },
                'order': {
                    'name': 'order',
                    'description': 'Order',
                    'schema': {
                        'type': 'string'
                    },
                },
                'metadata': {
                    'name': 'metadata',
                    'description': 'Show Metadata',
                    'schema': {
                        'type': 'boolean'
                    },
                },
            },
            responses={
                '200': {
                    'description': 'Extract Data', 
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/ExtractData'
                            },
                            'example': [
                              {'bank_ids': [], 'id': 1, 'name': 'YourCompany'},
                              {'bank_ids': [], 'id': 2, 'name': 'OdooBot'}
                            ],
                        },
                        
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def search_extract(
        self, 
        model, 
        domain=None, 
        fields=None, 
        limit=None, 
        offset=0, 
        order=None, 
        metadata=False,
        **kw
    ):
        domain = tools.common.parse_domain(domain)
        limit = limit and int(limit) or None
        offset = offset and int(offset) or None
        records = request.env[model].search(
            domain, limit=limit, offset=offset, order=order
        )
        context = dict(records.env.context)
        context.pop('active_test', False)
        records.with_context(context)
        return request.make_json_response(
            records.rest_extract_data(
                tools.common.parse_value(fields),
                metadata=metadata
            )
        )
     
    #----------------------------------------------------------
    # Create / Update / Delete
    #----------------------------------------------------------
    
    @core.http.rest_route(
        routes=build_route([
            '/create',
            '/create/<string:model>',
        ]), 
        methods=['POST'],
        protected=True,
        docs=dict(
            tags=['Model'], 
            summary='Create', 
            description='Creates new records.',
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
                'values': {
                    'name': 'values',
                    'description': 'Values',
                    'content': {
                        'application/json': {
                            'schema': {
                                'oneOf': [
                                    {'$ref': '#/components/schemas/RecordTuple'},
                                    {
                                        'type': 'array',
                                        'items': {
                                            '$ref': '#/components/schemas/RecordValues'
                                        }
                                    }
                                ],
                            },
                        },
                    },
                    'example': {'name': 'New Name'},
                },
            },
            responses={
                '200': {
                    'description': 'Records IDs', 
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs'
                            },
                            'example': [1, 2, 3]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def create(self, model, values=None, **kw):
        return request.make_json_response(
            request.env[model].create(
                tools.common.parse_value(values, {})
            ).ids
        )

    @core.http.rest_route(
        routes=build_route([
            '/write',
            '/write/<string:model>',
        ]), 
        methods=['PUT'],
        protected=True,
        docs=dict(
            tags=['Model'], 
            summary='Write', 
            description='Update records.',
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
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs',
                            },
                        },
                    },
                    'example': [1, 2, 3],
                },
                'values': {
                    'name': 'values',
                    'description': 'Values',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordValues'
                            },
                        },
                    },
                    'example': {'name': 'New Name'},
                },
            },
            responses={
                '200': {
                    'description': 'Records IDs', 
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs'
                            },
                            'example': [1, 2, 3]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def write(self, model, ids=None, values=None, **kw):
        records = request.env[model].browse(tools.common.parse_ids(ids))
        records.write(tools.common.parse_value(values, {}))
        return request.make_json_response(records.ids)



    @core.http.rest_route(
        routes=build_route([
            '/write_multi',
            '/write_multi/<string:model>',
        ]),
        methods=['PUT'],
        protected=True,
        docs=dict(
            tags=['Model'],
            summary='Write',
            description='Update records.',
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
                'values': {
                    'name': 'values',
                    'description': 'Values',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/MultiWriteValues'
                            },
                        },
                    },
                    'example': [[[1, 2], {'name': 'New Name'}]],
                },
            },
            responses={
                '200': {
                    'description': 'Records IDs',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs'
                            },
                            'example': [1, 2, 3]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def write_multi(self, model, values=None, **kw):
        values = tools.common.parse_value(values, [])
        record_ids = []
        for ids, vals in values:
            records = request.env[model].browse(
                tools.common.parse_ids(ids)
            )
            records.write(vals)
            record_ids.extend(records.ids)
        return request.make_json_response(record_ids)

    @core.http.rest_route(
        routes=build_route([
            '/create_update',
            '/create_update/<string:model>',
        ]), 
        methods=['POST'],
        protected=True,
        docs=dict(
            tags=['Model'], 
            summary='Create or Update',
            description='Creates or update a record.',
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
                'domain': {
                    'name': 'domain',
                    'description': 'Search Domain',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/Domain',
                            },
                        }
                    },
                    'example': [('email', '=', 'admin@yourcompany.example.com')],
                },
                'values': {
                    'name': 'values',
                    'description': 'Values',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordValues'
                            },
                        },
                    },
                    'example': {'name': 'New Name'},
                },
                'order': {
                    'name': 'order',
                    'description': 'Order',
                    'schema': {
                        'type': 'string'
                    },
                },
                'type': {
                    'name': 'type',
                    'description': 'Update Type',
                    'schema': {
                        'type': 'string',
                        'enum': ['limit', 'check', 'multi'],
                    }
                },
            },
            responses={
                '200': {
                    'description': 'Records IDs',
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs'
                            },
                            'example': [1, 2, 3]
                        }
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def create_update(
        self, model, domain, values=None, order=None, type='limit', **kw
    ):
        values = tools.common.parse_value(values, {})
        domain = tools.common.parse_domain(domain)
        limit = 1 if type == 'limit' else None
        records = request.env[model].search(
            domain, order=order, limit=limit
        )
        if type == 'check' and len(records) > 1:
            raise werkzeug.exceptions.BadRequest(
                'Multiple records were found for the given domain!'
            )
        if not records:
            records = request.env[model].create(values)
        else:
            records.write(values)
        return request.make_json_response(
            records.ids
        )

    @core.http.rest_route(
        routes=build_route([
            '/unlink',
            '/unlink/<string:model>',
        ]), 
        methods=['DELETE'],
        protected=True,
        docs=dict(
            tags=['Model'], 
            summary='Delete', 
            description='Delete records.',
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
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': '#/components/schemas/RecordIDs',
                            },
                        },
                    },
                    'example': [1, 2, 3],
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
                    }
                }
            },
            default_responses=['400', '401', '500'],
        ),
    )
    def unlink(self, model, ids=None, **kw):
        return request.make_json_response(
            request.env[model].browse(
                tools.common.parse_ids(ids)
            ).unlink()
        )
