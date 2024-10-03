/** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, onWillUnmount, useRef, onMounted } from "@odoo/owl";
import { OrderReprintReceipt } from "@pos_orders_all/app/screens/receipt_screen/receipt/order_reprint_receipt";

export class OrderReprintScreen extends Component {
    static components = { OrderReprintReceipt };
    static template = "pos_orders_all.OrderReprintScreen";

    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        this.printer = useService("printer");
        this.currentOrder = this.pos.get_order();
        this.buttonPrintReceipt = useRef("order-print-receipt-button");
    }

    back() {
        this.pos.showScreen('PosOrdersScreen', {
            'selected_partner_id': false,
        });
    }

    async printReceipt() {
        this.buttonPrintReceipt.el.className = "fa fa-fw fa-spin fa-circle-o-notch";
        const isPrinted = await this.printer.print(
            OrderReprintReceipt,
            {
                order: this.props.order,
                barcode: this.props.barcode,
                discount: this.props.discount,
                orderlines: this.props.orderlines,
                paymentlines: this.props.paymentlines,
                change: this.props.change,
                subtotal: this.props.subtotal,
                user_name: this.props.user_name,
                tax: this.props.tax,
                formatCurrency: this.env.utils.formatCurrency,
            },
            { webPrintFallback: true }
        );

        if (isPrinted) {
            this.currentOrder._printed = true;
        }

        if (this.buttonPrintReceipt.el) {
            this.buttonPrintReceipt.el.className = "fa fa-print";
        }
    }

}

registry.category("pos_screens").add("OrderReprintScreen", OrderReprintScreen);