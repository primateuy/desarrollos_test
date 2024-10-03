/** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, onWillUnmount, useRef, onMounted } from "@odoo/owl";

export class OrderReprintReceipt extends Component {
    static template = "pos_orders_all.OrderReprintReceipt";

    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        onMounted(() => {
            var order = this.pos.get_order();
            $("#barcode_print1").barcode(
                order.barcode, // Value barcode (dependent on the type of barcode)
                "code128" // type (string)
            );
        });
    }

    get receiptBarcode(){
        var order = this.pos.get_order();
        $("#barcode_print1").barcode(
            order.barcode, // Value barcode (dependent on the type of barcode)
            "code128" // type (string)
        );
        return true;
    }
}

registry.category("pos_screens").add("OrderReprintReceipt", OrderReprintReceipt);