/** @odoo-module **/

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Component } from "@odoo/owl";

export class SeePosOrderButton extends Component {
    static template = "pos_orders_all.SeePosOrderButton";

    setup() {
        this.pos = usePos();
    }
    
    click() {
        this.pos.showScreen('PosOrdersScreen', {
            'selected_partner_id': false,
        });
    }
}

ProductScreen.addControlButton({
    component: SeePosOrderButton,
    condition: function () {
        return this.pos.config.show_order;
    },
});
