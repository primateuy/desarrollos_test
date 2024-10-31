import json

from odoo import fields, models
from odoo.tools import ustr, config, date_utils
from odoo.http import Response

from odoo.addons.muk_rest.tools.common import parse_exception


class ResponseEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (bytes, bytearray)):
            return obj.decode()
        return date_utils.json_default(obj)


class RecordEncoder(ResponseEncoder):
    def default(self, obj):
        if isinstance(obj, models.BaseModel):
            return [(record.id, record.display_name) for record in obj]
        return ResponseEncoder.default(self, obj)


class LogEncoder(json.JSONEncoder):
    def iterencode(self, o, _one_shot=False):
        markers = {} if self.check_circular else None

        def limit_str(o):
            text = json.encoder.encode_basestring(o)
            limit = int(config.get('rest_logging_attribute_limit', 150))
            return '{}...'.format(text[:limit]) if limit and len(text) > limit else text

        if (_one_shot and json.encoder.c_make_encoder is not None and self.indent is None):
            _iterencode = json.encoder.c_make_encoder(
                markers, self.default, limit_str, self.indent,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, self.allow_nan
            )
        else:
            _iterencode = json.encoder._make_iterencode(
                markers, self.default, limit_str, self.indent, json.dumps,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, _one_shot
            )
        return _iterencode(o, 0)


def ustr_sql(value):
    return ustr(value, errors='replace').replace("\x00", "\uFFFD")


def limit_text_size(text):
    limit = int(config.get('rest_logging_content_limit', 25000))
    if limit and len(text) > limit:
        return '{}\n\n...'.format(text[:limit])
    return text


def encode_request(request):
    return limit_text_size(json.dumps(
        request.params, indent=4, cls=LogEncoder, default=lambda o: str(o)
    ))
    
            
def encode_response(response):
    if isinstance(response, Response):
        if response.mimetype == 'application/json':
            return json.dumps(
                json.loads(response.data), indent=4, 
                cls=LogEncoder, default=lambda o: str(o)
            )
        return limit_text_size(ustr_sql(response.data))
    if isinstance(response, Exception):
        json.dumps(parse_exception(response), indent=4, default=lambda o: str(o))
    return limit_text_size(ustr_sql(response))
