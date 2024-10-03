/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { PosInternalStockPopup } from "@pos_all_in_one/app/popup/pos_internal_stock_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component } from "@odoo/owl";

export class PosInternalTransferButton extends Component {
    static template = "pos_all_in_one.PosInternalTransferButton";

    setup() {
        this.pos = usePos();
    }

    click() {
		var self = this;
		self.pos.popup.add(PosInternalStockPopup, {});
	}
}

ProductScreen.addControlButton({
    component: PosInternalTransferButton,
    position: ["before", "SetFiscalPositionButton"],
    condition: function () {
        return this.pos.config.internal_transfer;
    },
});