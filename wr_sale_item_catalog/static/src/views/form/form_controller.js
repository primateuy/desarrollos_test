/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";

patch(FormController.prototype, "wr_sale_item_catalog.sale__form_control", {
    async beforeExecuteActionButton(clickParams) {
        var res = this._super(clickParams);
        if (clickParams && clickParams.special !== "cancel" && this.model.root.resModel == 'sale.order') {
            if($('tr.o_selected_row').length > 0){
                return false;
            }
            await this.model.root.save();
            await this.model.root.load();
            this.model.notify();
        }
        return res;
    }
});