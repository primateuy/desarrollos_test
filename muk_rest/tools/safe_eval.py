import werkzeug

from odoo.tools.safe_eval import wrap_module
from odoo import exceptions


responses = wrap_module(werkzeug.exceptions, [
    'HTTPException',
    'BadRequest',
    'ClientDisconnected',
    'SecurityError',
    'BadHost',
    'Unauthorized',
    'Forbidden',
    'NotFound',
    'MethodNotAllowed',
    'NotAcceptable',
    'RequestTimeout',
    'Conflict',
    'Gone',
    'LengthRequired',
    'PreconditionFailed',
    'RequestEntityTooLarge',
    'RequestURITooLarge',
    'UnsupportedMediaType',
    'RequestedRangeNotSatisfiable',
    'ExpectationFailed',
    'ImATeapot',
    'UnprocessableEntity',
    'Locked',
    'PreconditionRequired',
    'TooManyRequests',
    'RequestHeaderFieldsTooLarge',
    'UnavailableForLegalReasons',
    'InternalServerError',
    'NotImplemented',
    'BadGateway',
    'ServiceUnavailable',
    'GatewayTimeout',
    'HTTPVersionNotSupported',
])

exceptions = wrap_module(exceptions, [
    'UserError',
    'AccessDenied',
    'AccessError',
    'ValidationError',
])
