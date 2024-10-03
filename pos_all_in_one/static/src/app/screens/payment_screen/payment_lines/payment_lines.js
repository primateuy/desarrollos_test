/** @odoo-module */

import { PaymentScreenPaymentLines } from "@point_of_sale/app/screens/payment_screen/payment_lines/payment_lines";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(PaymentScreenPaymentLines.prototype, {
	setup() {
		super.setup();
		this.pos=usePos();
	},

	changeInput(event){
		let order = this.pos.get_order();
		let pl = order.selected_paymentline;
		var inputString = $("#Input").val();
		if(inputString){
			pl.set_pos_reference(inputString);
		}else{
			pl.set_pos_reference(pl.pos_reference);
		}
	},
	
});