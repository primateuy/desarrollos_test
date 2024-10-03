/** @odoo-module */

import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, useRef } from "@odoo/owl";
import { CouponPrint } from "@pos_orders_all/app/screens/product_screen/coupon_receipt_screen/coupon_print";
import { useService } from "@web/core/utils/hooks";

export class CouponReceiptScreen extends Component {
    static template = "pos_orders_all.CouponReceiptScreen";
    static components = { CouponPrint };
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        this.printer = useService("printer");
    }

    back() {
        this.props.resolve({ confirmed: false, payload: false });
        this.pos.closeTempScreen();
    }

    async printReceipt(receipt) {
        this.printer.print(
            CouponPrint,
            {
                data: this.props.data,
                formatCurrency: this.env.utils.formatCurrency,
            },
            { webPrintFallback: true }
        );
    }

	orderDone() {
        const { name, props } = this.nextScreen;
        this.pos.showScreen(name, props);
    }

  
}

registry.category("pos_screens").add("CouponReceiptScreen", CouponReceiptScreen);
