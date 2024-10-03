/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import {Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class XMLPosProductSummaryReceipt extends Component {
    static template = "pos_all_in_one.XMLPosProductSummaryReceipt";
    
    setup() {
        this.pos = usePos();
        this.orm = useService("orm");
        this.print_product();
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
			if(ord_st_date == false){
				$('#prod_dt_strt').show()
				setTimeout(function() {$('#prod_dt_strt').hide()},3000);
				return
			}
			else if(ord_end_date == false){
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
		self.get_product_receipt_render_env(output_summery_product, pro_st_date, pro_ed_date,prod_current_session);
	}



	get_pro_summery(){
		var output_summery_product = this.pos.get_order().get_screen_data('output_summery_product')
		return output_summery_product['props']['output_summery_product'];
	}
		
	get_product_st_date(){
		var pro_st_date = this.pos.get_order().get_screen_data('pro_st_date')
		return pro_st_date['props']['pro_st_date'];
		
	}
	get_product_ed_date(){
		var pro_ed_date = this.pos.get_order().get_screen_data('pro_ed_date')
		return pro_ed_date['props']['pro_ed_date'];

	}

	get_product_receipt_render_env(output_summery_product, pro_st_date, pro_ed_date,prod_current_session) {
		var is_current = this.pos.get_order().get_screen_data('prod_current_session')
		return {
			widget: this,
			pos: this.pos,
			prod_current_session : prod_current_session,
			p_summery: output_summery_product,
			p_st_date: pro_st_date,
			p_ed_date: pro_ed_date,
			date_p: (new Date()).toLocaleString(),
		};
	}
    
}