/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class ReturnOrderPopup extends AbstractAwaitablePopup {
    static template = "pos_orders_all.ReturnOrderPopup";
    static defaultProps = {
        confirmText: _t("Ok"),
        cancelKey: false,
        body: "",
    };

    setup() {
        super.setup();  
        this.pos = usePos();    
    }

    do_return_order(){
        let self = this;
        let selectedOrder = self.pos.get_order();
        let orderlines = self.props.orderlines;
        let order = self.props.order;
        let partner_id = false
        let client = false
        let create_order = true
        if (order && order.partner_id != null){
            partner_id = order.partner_id[0];
            client = self.pos.db.get_partner_by_id(partner_id);
        }

        let return_products = {};
        let exact_return_qty = {};
        let exact_entered_qty = {};
        let refund_qty = 0;

        let list_of_qty = $('.entered_item_qty');

        $.each(list_of_qty, function(index, value) {
            let entered_item_qty = $(value).find('input');
            let qty_id = parseFloat(entered_item_qty.attr('qty-id'));
            let line_id = parseFloat(entered_item_qty.attr('line-id'));
            let entered_qty = parseFloat(entered_item_qty.val());
            if(entered_qty){
                let returned_qty = parseFloat(entered_item_qty.attr('return-qty'));
                exact_return_qty = qty_id;
                exact_entered_qty = entered_qty || 0;
                let remained = qty_id - returned_qty;

                if(remained < entered_qty){
                    alert("Cannot Return More quantity than purchased");
                    create_order = false
                    return;
                }
                else{
                    if(!exact_entered_qty){
                        create_order = false
                        return;
                    }
                    else if (exact_return_qty >= exact_entered_qty){
                      return_products[line_id] = entered_qty;
                    }
                    else{
                        alert("Cannot Return More quantity than purchased");
                        create_order = false
                        return;
                    }
                }
            }
        });

        if(create_order){
            $.each( return_products, function( key, value ) {
                orderlines.forEach(function(ol) {
                    if(ol.id == key && value > 0){
                        let product = self.pos.db.get_product_by_id(ol.product_id[0]);
                        selectedOrder.add_product(product, {
                            quantity: - parseFloat(value),
                            price: ol.price_unit,
                            discount: ol.discount,
                            refunded_orderline_id: ol.id
                        });
                        selectedOrder.set_return_order_ref(ol.order_id[0]);
                        selectedOrder.selected_orderline.set_original_line_id(ol.id);
                    }
                });
            });
            selectedOrder.set_partner(client);
        }
        self.cancel();
        this.pos.showScreen("PosOrdersScreen");
        this.pos.showScreen("ProductScreen");
    }

    async getPayload() {
        return null;
    }
}
