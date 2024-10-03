/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class ImportSaleOrderPopup extends AbstractAwaitablePopup {
    static template = "pos_orders_all.ImportSaleOrderPopup";

    setup() {
        this.pos = usePos();
    }

    do_import(){
        let self = this;
        let selectedOrder = self.pos.get_order();
        let order = self.props.order;
        let orderlines = [];
        order.order_line.forEach(function(ol) {
            orderlines.push(self.pos.db.get_so_line_by_id[ol])
        });
        let imported = false;
        let partner_id = false
        let client = false
        if (order && order.partner_id != null){
            partner_id = order.partner_id[0];
            client = self.pos.db.get_partner_by_id(partner_id);
        }
        let import_products = {};
        let list_of_qty = $('.entered_item_qty');
        $.each(list_of_qty, function(index, value) {
            let entered_item_qty = $(value).find('input');
            let qty_id = parseFloat(entered_item_qty.attr('qty-id'));
            let line_id = parseFloat(entered_item_qty.attr('line-id'));
            let entered_qty = parseFloat(entered_item_qty.val());
            import_products[line_id] = entered_qty;
        });

        $.each( import_products, function( key, value ) {
            orderlines.forEach(function(ol) {
                if(ol.id == key && value > 0){
                    let product = self.pos.db.get_product_by_id(ol.product_id[0]);
                    if(product){
                        selectedOrder.add_product(product, {
                            quantity: parseFloat(value),
                            price: ol.price_unit,
                            discount: ol.discount,
                        });
                        selectedOrder.set_partner(client);
                        imported = true;
                    }else{
                        alert("please configure product for point of sale.");
                        return;
                    }
                }
            });
        });
        if(imported){
            selectedOrder.set_imported_sales(order.id);
        }
        this.props.close({ confirmed: false, payload: null });
        this.pos.showScreen("ProductScreen");
   }
}