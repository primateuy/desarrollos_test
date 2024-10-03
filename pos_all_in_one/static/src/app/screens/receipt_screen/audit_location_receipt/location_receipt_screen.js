/** @odoo-module */

import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useRef, useState, onWillStart, Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { LocationReceipt } from "@pos_all_in_one/app/screens/receipt_screen/audit_location_receipt/location_receipt";

export class LocationReceiptScreen extends ReceiptScreen {
    static template = "pos_all_in_one.LocationReceiptScreen";
    static components = { LocationReceipt }
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        this.printer = useService("printer");
    }

    back() {
        this.props.resolve({ confirmed: false, payload: false });
        this.pos.closeTempScreen();
        this.pos.showScreen('ProductScreen');
        
    }
	orderDone() {
		const { name, props } = this.nextScreen;
		this.showScreen(name, props);
	}

	async printReceipt() {
        this.buttonPrintReceipt.el.className = "fa fa-fw fa-spin fa-circle-o-notch";
        const isPrinted = await this.printer.print(
            LocationReceipt,
            {
                data: this.pos.get_order().export_for_printing(),
                formatCurrency: this.env.utils.formatCurrency,
                order: this.get_location_receipt_data(),
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
    
    get_location_receipt_data(){
		return {
			widget: this,
			pos: this.pos,
			ssn: this['props']['ssn'],
			loc_summery: this.get_loc_summery(),
			date: (new Date()).toLocaleString()

		};
		
	}

	get_loc_summery(){
		return this['props']['output_summery_location'];
	}
	

	get location_receipt_data() {
		return {
			widget: this,
			pos: this.pos,
			ssn: this['props']['ssn'],
			loc_summery: this.get_loc_summery(),
			date: (new Date()).toLocaleString()

		};
	}

    
}

registry.category("pos_screens").add("LocationReceiptScreen", LocationReceiptScreen);