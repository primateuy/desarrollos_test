import re
import inspect
import functools
import werkzeug
import textwrap

from inspect import Parameter
from collections import defaultdict

from odoo import conf, tools

from odoo.addons.muk_rest.tools.http import build_route
from odoo.addons.muk_rest.tools import common

DEFINED_DEFAULT_RESPONSES = {
    '400': {
        'description': 'The server could not process the request, probably due to an incorrect request syntax.',
    },
    '401': {
        'description': 'The server could not verify that you are authorized to access the requested URL.',
    },
    '500': {
        'description': 'An error occurred while the request was being processed and therefore it could not be executed completely.',
    },
}
DEFAULT_RESPONSE = {'200': {'description': 'Result', 'content': {'application/json': {'schema': {'type': 'object'}}}}}
DEFAULT_RESPONSES = defaultdict(lambda: {'content': {'application/json': {{'schema': {'type': 'object'}}}}})
DEFAULT_RESPONSES.update(DEFINED_DEFAULT_RESPONSES)
DEFAULT_RESPONSES.update(DEFAULT_RESPONSE)

COMPONENTS = {
    'schemas': {
        'DomainTuple': {
            'type': 'array',
            'items': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'boolean'},
                    {'type': 'number'},
                    {
                        'type': 'array',
                        'items': {
                            'anyOf': [
                                {'type': 'string'}, 
                                {'type': 'number'}
                            ]
                        },
                    }
                ]
            },
            'minItems': 3,
            'maxItems': 3,
            'description': 'A domain tuple consists of a field name, an operator and a value.'
        },
        'Domain': {
            'type': 'array',
            'items': {
                'anyOf': [
                    {'type': 'string'},
                    {'$ref': '#/components/schemas/DomainTuple'}
                
                ]
            },
            'description': 'A domain item consists either of a single operator or a tuple.'
        },
        'RecordIDs': {
            'type': 'array',
            'items': {
                'type': 'integer'
            },
            'description': 'A list of record IDs.'
        },
        'RecordFields': {
            'type': 'array',
            'items': {
                'type': 'string'
            },
            'description': 'A list of field names.'
        },
        'RecordValues': {
            'type': 'object',
            'description': 'A map of field names and their corresponding values.'
        },
        'RecordData': {
            'type': 'object',
            'properties': {
                'id': {
                    'type': 'integer',
                },
            },
            'additionalProperties': True,
            'description': 'A map of field names and their corresponding values.'
        },
        'RecordTuple': {
            'type': 'array',
            'items': {
                'anyOf': [
                    {'type': 'integer'},
                    {'type': 'string'},
                ]
            },
            'minItems': 2,
            'maxItems': 2,
            'description': 'A record tuple consists of the id and the display name of the record.'
        },
        'RecordTuples': {
            'type': 'array',
            'items': {
                '$ref': '#/components/schemas/RecordTuple'
            },
            'description': 'A list of record tuples.'
        },
        'UserContext': {
            'type': 'object',
            'properties': {
                'lang': {
                    'type': 'string',
                },
                'tz': {
                    'type': 'string',
                },
                'uid': {
                    'type': 'integer',
                },
            },
            'additionalProperties': True,
            'description': 'The current user context.'
        },
    }
}


def generate_security_docs(server_url):
    api_docs_authentication_methods = {}
    if common.ACTIVE_BASIC_AUTHENTICATION:
        api_docs_authentication_methods['BasicAuth'] = {
            'type': 'http',
            'scheme': 'basic',
            'description': 'Basic Authentication with username and password or access token.',
        }
    if common.ACTIVE_OAUTH2_AUTHENTICATION:
        api_docs_authentication_methods['OAuth2'] = {
            'type': 'oauth2',
            'description': 'OAuth2 Authentication',
            'flows': {
                'authorizationCode': {
                    'authorizationUrl': '{}{}'.format(server_url, build_route('/authentication/oauth2/authorize')[0]),
                    'tokenUrl': '{}{}'.format(server_url, build_route('/authentication/oauth2/token')[0]),
                    'refreshUrl': '{}{}'.format(server_url, build_route('/authentication/oauth2/token')[0]),
                    'scopes': {}
                },
                'implicit': {
                    'authorizationUrl': '{}{}'.format(server_url, build_route('/authentication/oauth2/authorize')[0]),
                    'refreshUrl': '{}{}'.format(server_url, build_route('/authentication/oauth2/token')[0]),
                    'scopes': {}
                },
                'password': {
                    'tokenUrl': '{}{}'.format(server_url, build_route('/authentication/oauth2/token')[0]),
                    'refreshUrl': '{}{}'.format(server_url, build_route('/authentication/oauth2/token')[0]),
                    'scopes': {}
                },
                'clientCredentials': {
                    'tokenUrl': '{}{}'.format(server_url, build_route('/authentication/oauth2/token')[0]),
                    'refreshUrl': '{}{}'.format(server_url, build_route('/authentication/oauth2/token')[0]),
                    'scopes': {}
                }
            }
        }
    return api_docs_authentication_methods


def generate_routing_docs(controllers):
    api_docs_path_values = {}
    api_docs_tag_values = set()
    api_docs_component_values = COMPONENTS

    def extract_docs(method):
        methods_seen = set()
        api_docs = dict(responses=DEFAULT_RESPONSE)
        routing = dict(auth='none', methods=["GET"], routes=[])
        for cla in reversed(method.__self__.__class__.mro()):
            func = getattr(cla, method.__name__, None)
            if func not in methods_seen:
                if hasattr(func, 'original_routing'):
                    routing.update(func.original_routing)
                if hasattr(func, 'api_docs'):
                    api_docs.update(func.api_docs)
            methods_seen.add(func)
        return api_docs, routing
    
    def parse_parameter(method, api_docs, path, is_protected):
        path_doc_parameters = dict()
        for param, param_vals in inspect.signature(method).parameters.items():
            if param_vals.kind not in [Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD]:
                path_doc_parameters[param] = {
                    'name': param,
                    'in': 'query',
                    'schema': {
                        'type': 'string'
                    }
                }
                if param_vals.default and param_vals.default is not Parameter.empty:
                    path_doc_parameters[param]['example'] = param_vals.default
        for param in map(lambda m: m.split(':')[-1], re.findall(r'<(.*?:?.+?)>', path)):
            if param not in path_doc_parameters:
                path_doc_parameters[param] = {'name': param}
            path_doc_parameters[param].update({
                'in': 'path',
                'required': True,
            })  
        if api_docs.get('parameter_context', is_protected):
            path_doc_parameters['with_context'] = {
                'name': 'with_context',
                'description': 'Context',
                'in': 'query',
                'schema': {
                    'type': 'string'
                },
            }
        if api_docs.get('parameter_company', is_protected):
            path_doc_parameters['with_company'] = {
                'name': 'with_company',
                'description': 'Current Company',
                'in': 'query',
                'schema': {
                    'type': 'integer'
                },
            }
        for param, param_vals in api_docs.get('parameter', {}).items():
            if param not in path_doc_parameters:
                path_doc_parameters[param] = {
                    'name': param,
                    'in': 'query',
                }
            path_doc_parameters[param].update(param_vals)
        for param in api_docs.get('exclude_parameters', []): 
            path_doc_parameters.pop(param, False)
        return path_doc_parameters
        
    def parse_docs(method, api_docs, routing):
        method_paths = api_docs.get('paths', routing['routes'])
        method_types = api_docs.get('methods', routing['methods'])
        parse_docs_path_values = dict()
        parse_docs_tag_values = set()
        for path in method_paths:
            path_doc_path = path
            path_doc_values = dict()
            path_doc_parameters = parse_parameter(
                method, api_docs, path, routing.get('protected', False)
            )
            for param in map(lambda m: m.split(':')[-1], re.findall(r'<(.*?:?.+?)>', path)):
                path_doc_path = re.sub(r'<(.*?:?{})>'.format(param), '{{{}}}'.format(param), path_doc_path)
            for method_type in map(lambda t: t.lower(), method_types):
                path_type_doc_values = {
                    'tags': api_docs.get('tags', []),
                    'summary': api_docs.get('summary', ""),
                    'description': api_docs.get('description', ""),
                    'responses': api_docs.get('responses', {}),
                    'parameters': api_docs.get('parameters', list(path_doc_parameters.values())),
                }
                if api_docs.get('requestBody', False):
                    path_type_doc_values['requestBody'] = api_docs['requestBody']
                if api_docs.get('default_responses', False):
                    for response in api_docs['default_responses']:
                        if response not in path_type_doc_values['responses']:
                            path_type_doc_values['responses'][response] = DEFAULT_RESPONSES[response]
                if routing.get('protected', False):
                    path_type_doc_values['security'] = []
                    if common.ACTIVE_BASIC_AUTHENTICATION:
                        path_type_doc_values['security'].append({
                            'BasicAuth': []
                        })
                    if common.ACTIVE_OAUTH2_AUTHENTICATION:
                        path_type_doc_values['security'].append({
                            'OAuth2': []
                        })
                if method_type in api_docs:
                    path_type_doc_values.update(api_docs[method_type])
                if '{}_{}'.format(method_type, path) in api_docs:
                    path_type_doc_values.update(api_docs['{}_{}'.format(method_type, path)])
                parse_docs_tag_values.update(path_type_doc_values.get('tags', []))
                path_doc_values[method_type] = path_type_doc_values
            parse_docs_path_values[path_doc_path] = path_doc_values
        return parse_docs_tag_values, parse_docs_path_values

    for controller in controllers:
        component = getattr(
            controller, 'API_DOCS_COMPONENTS', {}
        )
        for section, defs in component.items():
            if section in api_docs_component_values:
                api_docs_component_values[section].update(defs)
            else:
                api_docs_component_values[section] = defs
        for _, method in inspect.getmembers(controller, inspect.ismethod):
            if getattr(method, 'api_docs', False):
                api_docs, routing = extract_docs(method)
                if api_docs.get('show', True):
                    tags, paths = parse_docs(
                        method, api_docs, routing
                    )
                    api_docs_tag_values.update(tags)
                    api_docs_path_values.update(paths)
    return (
        list(filter(None, api_docs_tag_values)), 
        api_docs_path_values, 
        api_docs_component_values   
    )
         

def generate_docs(server_url, controllers):
    security = generate_security_docs(server_url)
    tags, paths, components = generate_routing_docs(controllers)
    return {
        'openapi': '3.0.0',
        'info': {
            'version': '1.0.0',
            'title': 'RESTful API Documentation',
            'description': textwrap.dedent("""\
                <p>
                    Enables a REST API for the Odoo server. The API has routes to authenticate
                    and retrieve a token. Afterwards, a set of routes to interact with the server
                    are provided. The API can be used by any language or framework which can make
                    an HTTP requests and receive responses with JSON payloads and works with both
                    the Community and the Enterprise Edition.
                </p>
                <p>
                    The API allows authentication via OAuth1 and OAuth2 as well as with username
                    and password, although an access key can also be used instead of the password.
                    The documentation only allows OAuth2 besides basic authentication. The API has
                    OAuth2 support for all 4 grant types. More information about the OAuth 
                    authentication can be found under the following links:
                </p>
                <ul>
                    <li>
                        <a href="https://tools.ietf.org/html/rfc5849" target="_blank">
                            OAuth1 - RFC5849
                        </a>
                    </li>
                    <li>
                        <a href="https://tools.ietf.org/html/rfc6749" target="_blank">
                            OAuth2 - RFC6749
                        </a>
                    </li>
                </ul>
            """),
            'license': {
                'name': 'MuK Proprietary License v1.0'
            },
            'contact': {
                'name': 'MuK IT',
                'url': 'https://www.mukit.at',
            },
        },
        'servers': [{
            'url': server_url,
        }],
        'paths': paths,
        'tags': [{'name': tag} for tag in tags],
        'components': dict(**components, securitySchemes=security),
    }
