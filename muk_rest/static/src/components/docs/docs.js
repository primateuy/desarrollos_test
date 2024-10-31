/** @odoo-module **/

const { whenReady } = owl;

async function SwaggerUI () {
    await whenReady();
    const swaggerUI = SwaggerUIBundle({
        url: odoo.rest.serverBaseUrl + '/rest/docs/api.json',
        oauth2RedirectUrl: odoo.rest.serverBaseUrl + '/rest/docs/oauth2/redirect',
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIStandalonePreset
        ],
        plugins: [
            SwaggerUIBundle.plugins.DownloadUrl
        ],
        layout: 'BaseLayout',
        operationsSorter: (elem1, elem2) => {
            let methodsOrder = ['get', 'post', 'put', 'delete', 'patch', 'options', 'trace'];
            let result = methodsOrder.indexOf(elem1.get('method')) - methodsOrder.indexOf(elem2.get('method'));
            return result === 0 ? elem1.get('path').localeCompare(elem2.get('path')) : result;
        },
        tagsSorter: 'alpha',
        requestInterceptor: (req) => {
            req.headers[odoo.rest.databaseHeader] = odoo.rest.databaseName;
            return req;
        },
    });

    swaggerUI.initOAuth({
        additionalQueryStringParams: {
            [odoo.rest.databaseParam]: odoo.rest.databaseName,
        },
    });
}

SwaggerUI();
