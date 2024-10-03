/** @odoo-module */

import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component } from "@odoo/owl";
import { XMLPosOrderSummaryReceipt } from "@pos_all_in_one/app/screens/receipt_screen/order_summary_receipt/xml_pos_order_summary_receipt";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";


export class OrderReceiptWidget extends ReceiptScreen {
    static template = "pos_all_in_one.OrderReceiptWidget";
    static components = { XMLPosOrderSummaryReceipt }

    setup() {
        super.setup(...arguments);
        this.pos = usePos();
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
            XMLPosOrderSummaryReceipt,
            {
                data: this.pos.get_order().export_for_printing(),
                formatCurrency: this.env.utils.formatCurrency,
                order: this.get_order_receipt_data(),
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
    
    get_order_receipt_data(){
		var is_current = this.pos.get_order().get_screen_data('order_current_session')
		return {
			widget: this,
			pos: this.pos,
			order_current_session :this['props']['order_current_session'],
			summery: this.get_summery(),
			st_date:this.get_order_st_date(),
			ed_date:this.get_order_ed_date(),
			date_o: (new Date()).toLocaleString(),
		};
		
	}

	get order_receipt_data() {
		var is_current = this.pos.get_order().get_screen_data('order_current_session')
		return {
			widget: this,
			pos: this.pos,
			order_current_session :this['props']['order_current_session'],
			summery: this.get_summery(),
			st_date:this.get_order_st_date(),
			ed_date:this.get_order_ed_date(),
			date_o: (new Date()).toLocaleString(),
		};
	}


	get_order_st_date(){
		return this['props']['ord_start_dt'];
	}

	get_order_ed_date(){
		return this['props']['ord_end_dt'];
	}

	get_summery(){
		return this['props']['output_summery'];
	}

    
}

registry.category("pos_screens").add("OrderReceiptWidget", OrderReceiptWidget);