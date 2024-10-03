/** @odoo-module */

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class LowStockLine extends Component {
    static template = "pos_orders_all.LowStockLine";
};
registry.category("pos_screens").add("LowStockLine", LowStockLine);
