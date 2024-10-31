/** @odoo-modules */

import { registry } from '@web/core/registry';

export const DocsService = {
    dependencies: ['rpc'],
    async start(env, { rpc }) {
        let dataProm;
        return {
            checkAccess(reload = false) {
                if (!dataProm || reload) {
                    dataProm = rpc('/rest/docs/check');
                }
                return dataProm;
            },
        };
    },
};

registry.category('services').add('rest_docs', DocsService);
