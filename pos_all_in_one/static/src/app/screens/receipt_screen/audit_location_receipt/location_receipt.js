/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import {Component } from "@odoo/owl";

export class LocationReceipt extends Component {
    static template = "pos_all_in_one.LocationReceipt";
    
    setup() {
        this.pos = usePos();
        
    }
    get highlight() {
        return this.props.order !== this.props.selectedOrder ? '' : 'highlight';
    }
}
