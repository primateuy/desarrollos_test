/** @odoo-module **/

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Component } from "@odoo/owl";

export class SaleOrderButton extends Component {
    static template = "pos_orders_all.SaleOrderButton";

    setup() {
        this.pos = usePos();
    }
    
    async click() {
        await this.pos.showScreen('SaleOrderScreen');
    }
}

ProductScreen.addControlButton({
    component: SaleOrderButton,
    condition: function () {
        return this.pos.config.check;
    },
});
