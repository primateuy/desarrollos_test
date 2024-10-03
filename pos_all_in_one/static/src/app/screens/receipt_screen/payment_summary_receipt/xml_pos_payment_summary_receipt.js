/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import {Component } from "@odoo/owl";

export class XMLPosPaymentSummaryReceipt extends Component {
    static template = "pos_all_in_one.XMLPosPaymentSummaryReceipt";
    
    setup() {
        this.pos = usePos();
        
    }
    
}

