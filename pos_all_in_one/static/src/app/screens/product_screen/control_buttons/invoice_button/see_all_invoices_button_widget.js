/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";


export class SeeAllInvoicesButtonWidget extends Component {
    static template = "pos_all_in_one.SeeAllInvoicesButtonWidget";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }

    async onClickInvoiceCustom() {
		var self = this;
		var currentOrder = self.pos.get_order()
		const currentPartner = currentOrder.get_partner();
		this.pos.showScreen('POSInvoiceScreen',
			{ partner: currentPartner }
		);
	}
}

ProductScreen.addControlButton({
    component: SeeAllInvoicesButtonWidget,
    condition: function () {
        return this.pos.config.allow_pos_invoice;
    },
});