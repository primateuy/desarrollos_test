/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, useRef } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class PopupProductWidget extends AbstractAwaitablePopup {
    static template = "pos_all_in_one.PopupProductWidget";

    setup() {
		super.setup();
		this.pos = usePos();
		this.orm = useService('orm');
		onMounted(() =>{
			var self = this;
			$('#prod_dt_strt').hide();
			$('#prod_dt_end').hide();
		});
	}
	go_back_screen() {
		this.pos.showScreen('ProductScreen');
		this.props.close({ confirmed: false, payload: null });
	}
	clickCurrentSession(){
		if ($('#prod_crnt_ssn').is(':checked')) {
			$('#prod_st_dt').hide();
			$('#prod_end_dt').hide();
		}
		else{
			$('#prod_st_dt').show();
			$('#prod_end_dt').show();
		}
	}
		
	print_product(){
		var self = this;
		var ord_st_date = $('#ord_st_date').val()
		var ord_end_date = $('#ord_end_date').val()
		var pro_st_date = $('#pro_st_date').val()
		var pro_ed_date = $('#pro_ed_date').val()
		var order = this.pos.get_order();
		var summery_product = [];
		var curr_session = self.pos.config.current_session_id[0];
		var prod_current_session = $('#prod_crnt_ssn').is(':checked')
		$('#prod_dt_strt').hide();
		$('#prod_dt_end').hide();

		if(prod_current_session == true)	
		{
			this.orm.call(
				'pos.order',
				'update_product_summery',
				[order['sequence_number'], pro_st_date, pro_ed_date,prod_current_session,curr_session],
			)
			.then(function(output_summery_product){
				summery_product = output_summery_product;
				self.save_product_summery_details(output_summery_product, pro_st_date, pro_ed_date,prod_current_session);
			});
		}
		else{
			if(!pro_st_date){
				$('#prod_dt_strt').show()
				setTimeout(function() {$('#prod_dt_strt').hide()},3000);
				return
			}
			else if(!pro_ed_date){
				$('#prod_dt_end').show()
				setTimeout(function() {$('#prod_dt_end').hide()},3000);
				return
			}
			else{
				this.orm.call(
					'pos.order',
					'update_product_summery',
					[order['sequence_number'], pro_st_date, pro_ed_date,prod_current_session,curr_session],
				)
				.then(function(output_summery_product){
					summery_product = output_summery_product;
					self.save_product_summery_details(output_summery_product, pro_st_date, pro_ed_date,prod_current_session);
				
				});
			}
		}
	}
	
	save_product_summery_details(output_summery_product, pro_st_date, pro_ed_date,prod_current_session){
		var self = this;
		this.props.close({ confirmed: false, payload: null });
		self.pos.showTempScreen('ProductReceiptWidget',{output_summery_product:output_summery_product, pro_st_date:pro_st_date, pro_ed_date:pro_ed_date,prod_current_session:prod_current_session});
	}
    
}
