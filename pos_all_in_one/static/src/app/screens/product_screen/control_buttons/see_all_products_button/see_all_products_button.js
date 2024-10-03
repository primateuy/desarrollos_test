/** @odoo-module **/

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Component } from "@odoo/owl";

export class SeeAllProductsButton extends Component {
    static template = "pos_all_in_one.SeeAllProductsButton";

    setup() {
        this.pos = usePos();
    }
    
    async click() {
        await this.pos.showTempScreen('PosProductScreen', {
            'selected_partner_id': false,
        });
    }
}

ProductScreen.addControlButton({
    component: SeeAllProductsButton,
    condition: function () {
        return this.pos.config.allow_pos_product_operations;
    },
});
