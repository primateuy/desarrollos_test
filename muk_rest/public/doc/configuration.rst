In case the module should be active in every database just change the auto install flag to ``True``. 
To activate the routes even if no database is selected the module should be loaded right at the server 
start. This can be done by editing the configuration file or passing a load parameter to the start script.

Parameter: ``--load=web,muk_rest``

To access the api in a multi database enviroment without a db filter, the name of the database must be
provided with each request via the db parameter.

Parameter: ``?db=<database_name>``

To configure this module, you need to:

#. Go to *Settings -> API -> Dashboard*. Here you can see an overview of all your APIs.
#. Click on *Create* or go to either *Restful API -> OAuth1* or *Restful API -> OAuth2* to create a new API.

To extend the API and to add your own routes, go to *Settings -> API -> Endpoints* and create a new endpoint.
An endpoint can be both public and protected and is then only accessible via authentication. An endpoint can
either evaluate a domain, perform a server action or execute python code.

Its possible to further customize the API via a set of parameters insde the config file. The following table
shows the possible parameters and their corresponding default value.

+----------------------------+--------------------------------------------------------------------------+-----------------------------------+
| Parameter                  | Description                                                              | Default                           |
+----------------------------+--------------------------------------------------------------------------+-----------------------------------+
| rest_default_cors          | Sets the CORS attribute on all REST routes                               | None                              |
+----------------------------+--------------------------------------------------------------------------+-----------------------------------+
| rest_docs_security_group   | Reference an access group to protect the API docs for unauthorized users | None                              |
+----------------------------+--------------------------------------------------------------------------+-----------------------------------+
| rest_docs_codegen_url      | Service to generate REST clients                                         | https://generator3.swagger.io/api |
+----------------------------+--------------------------------------------------------------------------+-----------------------------------+
| rest_authentication_basic  | Defines if the Basic authentication is active on the REST API            | True                              |
+----------------------------+--------------------------------------------------------------------------+-----------------------------------+
| rest_authentication_oauth1 | Defines if the OAuth1 authentication is active on the REST API           | True                              |
+----------------------------+--------------------------------------------------------------------------+-----------------------------------+
| rest_authentication_oauth2 | Defines if the OAUth2 authentication is active on the REST API           | True                              |
+----------------------------+--------------------------------------------------------------------------+-----------------------------------+

Parameters from an configuration file can be loaded via the ``--config`` command.
