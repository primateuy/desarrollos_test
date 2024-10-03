/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { Component, useEffect, useRef, onMounted } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(OrderReceipt.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        onMounted(() => {
            var order = this.pos.get_order();
            $("#barcode_print").barcode(
                order.barcode, // Value barcode (dependent on the type of barcode)
                "code128" // type (string)
            );
        });
    },

    get receiptBarcode(){
        var order = this.pos.get_order();
        return true;
    }
});
