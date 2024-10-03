/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(OrderWidget.prototype, {
    setup() {
        super.setup();
        this.pos = usePos();
    },

    get_total_qty(){
        var order = this.env.services.pos.get_order();
        let lines =  order.get_orderlines();
        var total_qty = 0;
        lines.map((line) => total_qty += line.quantity)
        return total_qty
    },

});