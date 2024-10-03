/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { ConnectionLostError } from "@web/core/network/rpc_service";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

patch(PaymentScreen.prototype, {

	setup() {
		super.setup()
        this.pos = usePos();
        if(this.pos.config.auto_check_invoice){
            this.currentOrder.set_to_invoice(true);
        }
	},
});