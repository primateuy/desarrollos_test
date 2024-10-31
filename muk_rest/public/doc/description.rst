Enables a REST API for the Odoo server. The API has routes to authenticate
and retrieve a token. Afterwards, a set of routes to interact with the server
are provided. The API can be used by any language or framework which can make
an HTTP requests and receive responses with JSON payloads and works with both
the Community and the Enterprise Edition.

The API allows authentication via OAuth1 and OAuth2 as well as with username
and password, although an access key can also be used instead of the password.
The documentation only allows OAuth2 besides basic authentication. The API has
OAuth2 support for all 4 grant types. More information about the OAuth 
authentication can be found under the following links:

* `OAuth1 - RFC5849 <https://tools.ietf.org/html/rfc5849>`_
* `OAuth2 - RFC6749 <https://tools.ietf.org/html/rfc6749>`_
