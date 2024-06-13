/** @odoo-module */

import { Record } from "@web/views/relational_model";

export class SaleCatalogProductRecord extends Record {
    /**
     * @override
     */
    async _update(changes) {
        if ("sale_catalog_quantity" in changes && Object.keys(changes).length === 1) {
            const action = await this.model.orm.call(
                this.resModel,
                "set_sale_catalog_quantity",
                [this.resId, changes.sale_catalog_quantity],
                { context: this.context }
            );
            if (action && action !== true) {
                await this.model.action.doAction(action, {
                    onClose: () => this.model.reloadRecords(this),
                });
            } else {
                await this.model.reloadRecords(this);
            }
            return;
        }
        super._update(changes);
    }
}
