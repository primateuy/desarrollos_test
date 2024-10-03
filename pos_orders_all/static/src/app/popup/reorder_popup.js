/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class ReOrderPopup extends AbstractAwaitablePopup {
    static template = "pos_orders_all.ReOrderPopup";
    static defaultProps = {
        confirmText: _t("Ok"),
        cancelKey: false,
        body: "",
    };

    setup() {
        super.setup();  
        this.pos = usePos();    
    }

    do_reorder(){
        let self = this;
        let selectedOrder = self.pos.get_order();
        let orderlines = self.props.orderlines;
        let order = self.props.order;
        let partner_id = false
        let client = false
        if (order && order.partner_id != null){
            partner_id = order.partner_id[0];
            client = self.pos.db.get_partner_by_id(partner_id);
        }
        let reorder_products = {};
        let list_of_qty = $('.entered_item_qty');
        $.each(list_of_qty, function(index, value) {
            let entered_item_qty = $(value).find('input');
            let qty_id = parseFloat(entered_item_qty.attr('qty-id'));
            let line_id = parseFloat(entered_item_qty.attr('line-id'));
            let entered_qty = parseFloat(entered_item_qty.val());
            reorder_products[line_id] = entered_qty;
        });
        
        $.each( reorder_products, function( key, value ) {
            orderlines.forEach(function(ol) {
                if(ol.id == key && value > 0){
                    let product = self.pos.db.get_product_by_id(ol.product_id[0]);
                    selectedOrder.add_product(product, {
                        quantity: parseFloat(value),
                        price: ol.price_unit,
                        discount: ol.discount,
                    });
                }
            });
        });

        selectedOrder.set_partner(client);
        self.cancel();
        this.pos.showScreen("PosOrdersScreen");
        this.pos.showScreen("ProductScreen");
    }

    async getPayload() {
        return null;
    }
}
