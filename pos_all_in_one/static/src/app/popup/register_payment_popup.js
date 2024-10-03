/** @odoo-module **/

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";

export class RegisterPaymentPopupWidget extends AbstractAwaitablePopup {
    static template = "pos_all_in_one.RegisterPaymentPopupWidget";

    setup() {
        super.setup();
        this.pos = usePos();
        this.popup = useService("popup");
        this.orm = useService("orm");
        this.partner = this.partner;
    }

    cancel() {
        this.props.close({ confirmed: false});
		this.pos.showTempScreen('PartnerListScreen');
    }

    register_payment() {
		var self = this;
		var partner = this.props.partner || false;
		
		var payment_type = $('#payment_type').val();
		var entered_amount = $("#entered_amount").val();
		var entered_note = $("#entered_note").val();
		let rpc_result = false;

		if(entered_amount == ''){
			alert('Please Enter Amount !!!!');
		}else if (entered_amount == 0){
			alert('Amount should not be zero !!!!');
		}else{
			rpc_result = this.orm.call(
				'pos.create.customer.payment',
				'create_customer_payment',
				[partner ? partner.id : 0, partner ? partner.id : 0, payment_type, entered_amount, entered_note],
			).then(function(output) {
				alert('Payment has been Registered for this Customer !!!!');
				self.props.close({ confirmed: false});
				self.pos.showScreen('ProductScreen');
			});
		}		
	}
}