/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Component } from "@odoo/owl";
import { PopupOrderWidget } from "@pos_all_in_one/app/popup/order_summary_popup";

export class ReportOrderButtonWidget extends Component {
	static template = "pos_all_in_one.ReportOrderButtonWidget";

	setup() {
		this.pos = usePos();
	}

	async onClick(){
		var self = this;
		self.pos.popup.add(PopupOrderWidget,{
			'title': 'Order Summary',
		});
	}
   
}

ProductScreen.addControlButton({
	component: ReportOrderButtonWidget,
	position: ["before", "SetFiscalPositionButton"],
	condition: function () {
		return this.pos.config.order_summery;
	},
});