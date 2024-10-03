/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component, onMounted, useRef } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class PopupCategoryWidget extends AbstractAwaitablePopup {
    static template = "pos_all_in_one.PopupCategoryWidget";
    
    setup() {
		super.setup();
		this.pos = usePos();
		this.orm = useService('orm');
		
		onMounted(() =>{
			var self = this;
			$('#categ_dt_strt').hide();
			$('#categ_dt_end').hide();
		});
	}
	back() {
		this.pos.showScreen('ProductScreen');
		this.props.close({ confirmed: false, payload: null });
	}

	clickCurrentSession(){
		if ($('#categ_crnt_ssn').is(':checked')) {
			$('#ct_st_dt').hide();
			$('#ct_end_dt').hide();
		}
		else{
			$('#ct_st_dt').show();
			$('#ct_end_dt').show();
		}
	}

	async print_category_summary(){
		var self = this;
		var categ_st_date = $('#categ_st_date').val()
		var categ_ed_date = $('#categ_ed_date').val()
		var category_summary = [];
		var current_lang = self.context
		var curr_session = self.pos.config.current_session_id[0];
		var categ_current_session = $('#categ_crnt_ssn').is(':checked')
		$('#categ_dt_strt').hide();
		$('#categ_dt_end').hide();

		if(categ_current_session == true)	
		{
			await self.orm.call(
				'pos.report.category', 
				'get_category_pos_order', 
				[self.pos.order_sequence,categ_st_date,categ_ed_date,curr_session,categ_current_session], 
			).then(function(data){ 
				category_summary = data;
				var make_total = [];
				var final_total = null;

				for(var i=0;i<category_summary.length;i++){
					make_total.push(category_summary[i].sum)
					final_total = make_total.reduce(function(acc, val) { return acc + val; });
				}
				self.props.close({ confirmed: false, payload: null });
				self.pos.showTempScreen('CategoryReceiptWidget',{
					category_summary:category_summary,
					start_date_categ:categ_st_date,
					end_date_categ:categ_ed_date,
					final_total:final_total,
					categ_current_session:categ_current_session,
				});
			});
		}
		else{
			if(categ_st_date == false){
				$('#categ_dt_strt').show()
				setTimeout(function() {$('#categ_dt_strt').hide()},3000);
				return
			}
			else if(categ_ed_date == false){
				$('#categ_dt_end').show()
				setTimeout(function() {$('#categ_dt_end').hide()},3000);
				return
			}
			else{
				await self.orm.call(
					'pos.report.category', 
					'get_category_pos_order', 
					[self.pos.order_sequence,categ_st_date,categ_ed_date,curr_session,categ_current_session], 
				).then(function(data){ 
					category_summary = data;
					var make_total = [];
					var final_total = null;

					for(var i=0;i<category_summary.length;i++){
						make_total.push(category_summary[i].sum)
						final_total = make_total.reduce(function(acc, val) { return acc + val; });
					}
					self.props.close({ confirmed: false, payload: null });
					self.pos.showTempScreen('CategoryReceiptWidget',{
						category_summary:category_summary,
						start_date_categ:categ_st_date,
						end_date_categ:categ_ed_date,
						final_total:final_total,
						categ_current_session:categ_current_session,
					});
				});
			}
		}
	}

}
