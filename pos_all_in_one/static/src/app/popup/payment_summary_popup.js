/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, useRef } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class PopupPaymentWidget extends AbstractAwaitablePopup {
    static template = "pos_all_in_one.PopupPaymentWidget";
    setup() {
		super.setup();
		this.pos = usePos();
		this.orm = useService('orm');
		this.render_payment_summary();
		
		onMounted(() =>{
			var self = this;
			$('#dt_strt').hide();
			$('#dt_end').hide();
		});
	}
	go_back_screen() {
		this.pos.showScreen('ProductScreen');
		this.props.close({ confirmed: false, payload: null });
	}

	clickCurrentSession(){
		if ($('#pymnt_crnt_ssn').is(':checked')) {
			$('#strt_dt').hide();
			$('#end_dt').hide();
		}
		else{
			$('#strt_dt').show();
			$('#end_dt').show();
		}
	}

	async render_payment_summary(){
		$('#dt_strt').hide();
		$('#dt_end').hide();

		$('#pymnt_crnt_ssn').click(function() {
			if ($('#pymnt_crnt_ssn').is(':checked')) {
				$('#strt_dt').hide();
				$('#end_dt').hide();
			}
			else{
				$('#strt_dt').show();
				$('#end_dt').show();
			}
		});

		var self = this;
		var is_current_session = $('#pymnt_crnt_ssn').is(':checked')
		var pay_st_date = $('#pay_st_date').val()
		var pay_ed_date = $('#pay_ed_date').val()
		var smry_payment = $('#smry_payment').val()

		var order = this.pos.get_order();
		var config_id = self.pos.config_id
		var curr_session = self.pos.config.current_session_id[0];
		var payment_summary = [];
		var cashier = this.pos.get_cashier();
		var cashier_id = this.pos.get_cashier_user_id();

		$('#dt_strt').hide();
		$('#dt_end').hide();

		if(is_current_session == true)	
		{
			await this.orm.call(
				'pos.report.payment', 
				'get_crnt_ssn_payment_pos_order', 
				[1,smry_payment,cashier,cashier_id,config_id,curr_session,is_current_session,pay_st_date,pay_ed_date], 
			).then(function(data){ 
				var payments = data[2];
				payment_summary = data[1];
				var final_total = data[0];
				
				self.props.close({ confirmed: false, payload: null });

				self.pos.showTempScreen('PaymentReceiptWidget',{
					payment_summary:payment_summary,
					final_total:final_total,
					is_current_session:is_current_session,
					payments : payments,
					smry_payment : smry_payment,
				});
			});
		}
		else{
			if(!pay_st_date){
				$('#dt_strt').show()
				setTimeout(function() {$('#dt_strt').hide()},3000);
				return
			}
			else if(!pay_ed_date){
				$('#dt_end').show()
				setTimeout(function() {$('#dt_end').hide()},3000);
				return
			}
			else{

				await this.orm.call(
					'pos.report.payment', 
					'get_crnt_ssn_payment_pos_order', 
					[1,smry_payment,cashier,cashier_id,config_id,curr_session,is_current_session,pay_st_date,pay_ed_date], 
				).then(function(data){ 
					var payments = data[2];
					payment_summary = data[1];
					var final_total = data[0];
					
					self.props.close({ confirmed: false, payload: null });
					self.pos.showTempScreen('PaymentReceiptWidget',{
						payment_summary:payment_summary,
						final_total:final_total,
						is_current_session:is_current_session,
						payments : payments,
						start_date_pay:pay_st_date,
						end_date_pay:pay_ed_date,
						smry_payment : smry_payment,
					});
				});
				return
			}

		}
	}
}