/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, useRef } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class PopupOrderWidget extends AbstractAwaitablePopup {
    static template = "pos_all_in_one.PopupOrderWidget";
   
    setup() {
		super.setup();
		this.pos = usePos();
		this.orm = useService('orm');
		onMounted(() =>{
			$('#ordr_dt_strt').hide();
			$('#ordr_dt_end').hide();
		});
	}

	go_back_screen() {
		this.pos.showScreen('ProductScreen');
		this.props.close({ confirmed: false, payload: null });
	}
	clickCurrentSession(){
		if ($('#ordr_crnt_ssn').is(':checked')) {
			$('#order_st').hide();
			$('#order_end').hide();
		}
		else{
			$('#order_st').show();
			$('#order_end').show();
		}
	}
		
	async print_order (){
		var self = this;
		var ord_st_date = $('#ord_st_date').val()
		var ord_end_date = $('#ord_end_date').val()
		var ord_state = $('#ord_state').val()
		var order = self.pos.get_order();
		var summery_order = [];
		var curr_session = self.pos.config.current_session_id[0];
		var order_current_session = $('#ordr_crnt_ssn').is(':checked')
		$('#ordr_dt_strt').hide();
		$('#ordr_dt_end').hide();
		if(order_current_session == true)	
		{
			await this.orm.call(
					'pos.order',
					'update_order_summery',
					[order['sequence_number'], ord_st_date, ord_end_date, ord_state,curr_session,order_current_session],
			).then(function(output_summery){
				summery_order = output_summery;
				self.save_summery_details(output_summery, ord_st_date, ord_end_date,order_current_session);
			
			});
		}
		else{
			if(ord_st_date == false){
				$('#ordr_dt_strt').show()
				setTimeout(function() {$('#ordr_dt_strt').hide()},3000);
				return
			}
			else if(ord_end_date == false){
				$('#ordr_dt_end').show()
				setTimeout(function() {$('#ordr_dt_end').hide()},3000);
				return
			}
			else{
				await this.orm.call(
					'pos.order',
					'update_order_summery',
					[order['sequence_number'], ord_st_date, ord_end_date,ord_state,curr_session,order_current_session],
				).then(function(output_summery){
					summery_order = output_summery;
					self.save_summery_details(output_summery, ord_st_date, ord_end_date,order_current_session);
				
				});
			}
		}
		
	}

	save_summery_details(output_summery, ord_st_date, ord_end_date,order_current_session){
		var self = this;
		this.props.close({ confirmed: false, payload: null });
		self.pos.showTempScreen('OrderReceiptWidget',{output_summery:output_summery, ord_start_dt:ord_st_date, ord_end_dt:ord_end_date,order_current_session:order_current_session});
	}
    
}