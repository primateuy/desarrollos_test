/** @odoo-module */

import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component } from "@odoo/owl";
import { XMLPosPaymentSummaryReceipt } from "@pos_all_in_one/app/screens/receipt_screen/payment_summary_receipt/xml_pos_payment_summary_receipt";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";


export class PaymentReceiptWidget extends ReceiptScreen {
    static template = "pos_all_in_one.PaymentReceiptWidget";
    static components = { XMLPosPaymentSummaryReceipt } 
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
    }

    back() {
        this.props.resolve({ confirmed: false, payload: false });
        this.pos.closeTempScreen();
        this.pos.showScreen('ProductScreen');
    }

    async printReceipt() {
        this.buttonPrintReceipt.el.className = "fa fa-fw fa-spin fa-circle-o-notch";
        const isPrinted = await this.printer.print(
            XMLPosPaymentSummaryReceipt,
            {
                data: this.pos.get_order().export_for_printing(),
                formatCurrency: this.env.utils.formatCurrency,
                order: this.get_payment_receipt_data(),
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
    
    get_payment_receipt_data(){
		var self = this;
		var is_current_session =  this['props']['is_current_session']
		if(is_current_session == true)
		{
			return {
				widget: this,
				pos: this.env.pos,
				payments : this['props']['payments'],
				is_current_session:is_current_session,
				pay_summary: this.get_payment_summery(),
				final_total:this.get_payment_final_total(),
				date_pay: (new Date()).toLocaleString(),
				smry_payment : this['props']['smry_payment'],
			};
		}
		else{
			return {
				widget: this,
				pos: this.env.pos,
				is_current_session:is_current_session,
				pay_summary: this.get_payment_summery(),
				payments : this['props']['payments'],
				final_total:this.get_payment_final_total(),
				smry_payment : this['props']['smry_payment'],
				st_date_pay:this.get_payment_st_date(),
				ed_date_pay:this.get_payment_ed_date(),
				st_month_pay:this.get_payment_st_month(),
				ed_month_pay:this.get_payment_ed_month(),
				date_pay: (new Date()).toLocaleString(),
			};
		}
		
	}
	
    get payment_receipt_data() {
		var self = this;
		var is_current_session =  this['props']['is_current_session']
		if(is_current_session == true)
		{
			return {
				widget: this,
				pos: this.env.pos,
				payments : this['props']['payments'],
				is_current_session:is_current_session,
				pay_summary: this.get_payment_summery(),
				final_total:this.get_payment_final_total(),
				date_pay: (new Date()).toLocaleString(),
				smry_payment : this['props']['smry_payment'],
			};
		}
		else{
			return {
				widget: this,
				pos: this.env.pos,
				is_current_session:is_current_session,
				pay_summary: this.get_payment_summery(),
				payments : this['props']['payments'],
				final_total:this.get_payment_final_total(),
				smry_payment : this['props']['smry_payment'],
				st_date_pay:this.get_payment_st_date(),
				ed_date_pay:this.get_payment_ed_date(),
				st_month_pay:this.get_payment_st_month(),
				ed_month_pay:this.get_payment_ed_month(),
				date_pay: (new Date()).toLocaleString(),
			};
		}
		
	}

	get_payment_summery(){
		return this['props']['payment_summary'];
	}

	get_payment_final_total () {
		return this['props']['final_total'];
	}

	get_payment_st_date (){
		var st_date1 = this['props']['start_date_pay']
		var st_date = st_date1.split("-")
		
		var st_date_d = st_date[2];
		var st_date_m = st_date[1];
		var st_date_y = st_date[0];
		var full_st_date = st_date_d+'-'+st_date_m+'-'+st_date_y
		return full_st_date; 
	}

	get_payment_ed_date (){
		var ed_date1 = this['props']['end_date_pay']
		var ed_date = ed_date1.split("-")

		var ed_date_d = ed_date[2];
		var ed_date_m = ed_date[1];
		var ed_date_y = ed_date[0];
		var full_ed_date = ed_date_d+'-'+ed_date_m+'-'+ed_date_y
		return full_ed_date;
	}


	get_payment_st_month(){
		var st_date1 = this['props']['start_date_pay']
		var st_date = st_date1.split("-")
		
		var monthNames = ["",
			"January", "February", "March",
			"April", "May", "June", "July",
			"August", "September", "October",
			"November", "December"
		];

		var st_date_m_index = st_date[1];
		var st_date_split = st_date_m_index.split('')
		
		if(st_date_split[0] > '0'){
			st_date_m_index = st_date_m_index
		}else{
			st_date_m_index = st_date_m_index.split('')[1]
		}
		var st_date_y = st_date[0];

		return monthNames[st_date_m_index]+'-'+st_date_y;
	}

	get_payment_ed_month (){
		var ed_date1 = this['props']['end_date_pay']
		var ed_date = ed_date1.split("-")

		var monthNames = ["",
			"January", "February", "March",
			"April", "May", "June", "July",
			"August", "September", "October",
			"November", "December"
		];

		var ed_date_m_index = ed_date[1];
		var ed_date_split = ed_date_m_index.split('')
		if(ed_date_split[0] > '0'){
			ed_date_m_index = ed_date_m_index
		}else{
			ed_date_m_index = ed_date_m_index.split('')[1]
		}
		var ed_date_y = ed_date[0];
		return monthNames[ed_date_m_index]+'-'+ed_date_y;
	}

    
}

registry.category("pos_screens").add("PaymentReceiptWidget", PaymentReceiptWidget);