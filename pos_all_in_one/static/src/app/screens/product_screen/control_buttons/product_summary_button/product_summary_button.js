/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Component } from "@odoo/owl";
import { PopupProductWidget } from "@pos_all_in_one/app/popup/product_summary_popup";

export class ReportProductButtonWidget extends Component {
	static template = "pos_all_in_one.ReportProductButtonWidget";

	setup() {
		this.pos = usePos();
	}

	async onClick(){
		var self = this;
		self.pos.popup.add(PopupProductWidget,{
		    'title': 'Product Summary',
		});
	}
}

ProductScreen.addControlButton({
	component: ReportProductButtonWidget,
	position: ["before", "SetFiscalPositionButton"],
	condition: function () {
		return this.pos.config.product_summery;
	},
});