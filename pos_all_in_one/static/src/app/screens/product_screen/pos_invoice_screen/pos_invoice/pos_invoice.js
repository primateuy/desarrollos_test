/** @odoo-module */

import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component} from "@odoo/owl";

export class POSInvoice extends Component {
    static template = "pos_all_in_one.POSInvoice";

    setup() {
        this.pos = usePos();
    }

    get highlight() {
        return this.props.order !== this.props.selectedPosOrder ? '' : 'highlight';
    }
}

registry.category("pos_screens").add("POSInvoice", POSInvoice);
