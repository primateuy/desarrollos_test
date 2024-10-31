import logging

_logger = logging.getLogger(__name__)

oauth1 = False
oauth2 = False

oauth1_provider = False
oauth2_provider = False

try:
    import oauthlib
    
    from . import oauth1
    from . import oauth2

    from oauthlib.oauth1 import WebApplicationServer as OAuth1Server
    from oauthlib.oauth2 import Server as OAuth2Server
    
    from odoo.addons.muk_rest.validators.oauth1 import OAuth1RequestValidator
    from odoo.addons.muk_rest.validators.oauth2 import OAuth2RequestValidator

    oauth1_provider = OAuth1Server(OAuth1RequestValidator())
    oauth2_provider = OAuth2Server(OAuth2RequestValidator())
except ImportError:
    _logger.warning("The Python library oauthlib is not installed, OAuth of the REST API wont work.")
