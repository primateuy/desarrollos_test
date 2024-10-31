from urllib.parse import urlencode
from urllib.parse import urlparse, urlunparse, parse_qs

from odoo.addons.muk_rest.tools import common


def build_route(route):
    param_routes = route
    if not isinstance(route, list):
        param_routes = [route]
    api_routes = []
    for item in param_routes:
        api_routes.append('{}{}'.format(common.BASE_URL, item))
    return api_routes


def clean_query_params(query, clean_db=True, clean_debug=True):
    cleaned_params = {}
    parsed_url = urlparse(query)
    params = parse_qs(parsed_url.query)
    for key, value in params.items():
        invalid_param_check = any(
            param and not set(param) <= common.SAFE_URL_CHARS or \
                common.INVALID_HEX_PATTERN.search(param) or \
                (clean_debug and key == 'debug') or \
                (clean_db and key == 'db')
            for param in value
        )
        if not invalid_param_check and not ():
            cleaned_params[key] = value
    parsed_url = parsed_url._replace(
        query=urlencode(cleaned_params, True)
    )
    return urlunparse(parsed_url)
