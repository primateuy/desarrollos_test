/** @odoo-module */

import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component } from "@odoo/owl";
import { SaleOrderDetailPopup } from "@pos_orders_all/app/popup/sale_order_details_popup";
import { ImportSaleOrderPopup } from "@pos_orders_all/app/popup/import_sale_order_popup";

export class SaleOrdersLine extends Component {
    static template = "pos_orders_all.SaleOrdersLine";

    setup() {
        this.pos = usePos();
    }

    importSale(order){
        let self = this;
        let pos_lines = [];
        order.order_line.forEach(function(ol) {
            pos_lines.push(self.env.services.pos.db.get_so_line_by_id[ol])
        });

        this.pos.popup.add(ImportSaleOrderPopup,{
             'order': order,
             'orderline':pos_lines,
        });
    }

    showDetails(order){
        let self = this;
        let pos_lines = [];
        order.order_line.forEach(function(ol) {
            pos_lines.push(self.env.services.pos.db.get_so_line_by_id[ol])
        });
        
        this.pos.popup.add(SaleOrderDetailPopup,{
             'order': order,
             'orderline':pos_lines,
        });
    }
    get highlight() {
        return this.props.order !== this.props.selectedSaleOrder ? '' : 'highlight';
    }
}

registry.category("pos_screens").add("SaleOrdersLine", SaleOrdersLine);