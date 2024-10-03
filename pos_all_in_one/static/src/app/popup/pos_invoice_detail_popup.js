/** @odoo-module **/

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { RegisterInvoicePaymentPopupWidget } from "@pos_all_in_one/app/popup/register_invoice_payment_popup"

export class PosInvoiceDetail extends AbstractAwaitablePopup {
    static template = "pos_all_in_one.PosInvoiceDetail";

    setup() {
        super.setup();
        this.pos = usePos();
        this.popup = useService("popup");
        this.partner = this.partner;
    }

    go_back_screen() {
		this.props.close({ confirmed: false});
		this.pos.showScreen('ProductScreen');
	}

	async register_payment() {
		var self = this;
		var invoice = this.props.order;
		this.props.close({ confirmed: false});
		this.popup.add(RegisterInvoicePaymentPopupWidget, {'invoice': this.props.order});
	}
}