/** @odoo-module */

import { PartnerListScreen } from "@point_of_sale/app/screens/partner_list/partner_list";
import { RegisterPaymentPopupWidget } from "@pos_all_in_one/app/popup/register_payment_popup";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(PartnerListScreen.prototype, {
	setup() {
        super.setup();
        this.popup = useService("popup");
	},

	registerPayment(partner){
		this.popup.add(RegisterPaymentPopupWidget, {'partner': partner});
	}
});