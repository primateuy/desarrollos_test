/** @odoo-module */

import { KanbanRecord } from '@web/views/kanban/kanban_record';

export class SaleCatalogProductKanbanRecord extends KanbanRecord {
    onGlobalClick(ev) {
        if (ev.target.closest('.o_sale_catalog_product_quantity')) {
            return;
        }
        const { openAction, fieldNodes } = this.props.archInfo;
        const { sale_catalog_quantity } = fieldNodes;
        if (openAction && ['sale_catalog_quantity', 'sale_catalog_remove_quantity'].includes(openAction.action) && catalog_quantity && sale_catalog_quantity.widget === 'catalog_product_quantity') {
            let sale_catalogProductQty = this.props.record.data.sale_catalog_quantity;
            if (openAction.action === 'sale_catalog_add_quantity') {
                sale_catalogProductQty++;
            } else {
                sale_catalogProductQty--;
            }
            this.props.record.update({ sale_catalog_quantity: catalogProductQty })
            return;
        }
        return super.onGlobalClick(ev);
    }
}
