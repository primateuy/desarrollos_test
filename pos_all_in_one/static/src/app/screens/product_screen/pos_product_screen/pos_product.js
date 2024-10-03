/** @odoo-module */

import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component } from "@odoo/owl";

export class POSProduct extends Component {
    static template = "pos_all_in_one.POSProduct";
    setup() {
        super.setup();
        this.order = this.props.order;
        this.pos = usePos();
    }

    get highlight() {
        return this.props.order !== this.props.selectedSaleOrder ? '' : 'highlight';
    }
}

registry.category("pos_screens").add("POSProduct", POSProduct);