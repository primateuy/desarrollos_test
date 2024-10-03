/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { Component, onMounted, useRef } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";

export class PopupLocationWidget extends AbstractAwaitablePopup {
    static template = "pos_all_in_one.PopupLocationWidget";
    
   	setup() {
		super.setup();
		this.pos = usePos();
		this.orm = useService("orm");
		onMounted(() =>{
			var self = this;
			$('#select_ssn').hide();
			$('#select_loc').hide();
		});
	}

	go_back_screen() {
		this.pos.showScreen('ProductScreen');
		this.props.close({ confirmed: false, payload: null });

	}

	get pos_sessions(){
		let sessions = this.pos.pos_sessions;
		let pos_sessions = [];
		$.each(sessions, function( i, session ){
			if(session){
				pos_sessions.push(session)
			}
		});
		return pos_sessions;
	}

	get locations(){
		let pos_locations = this.pos.locations;
		let locations = [];
		$.each(pos_locations, function( i, loc ){
			if(loc){
				locations.push(loc)
			}
		});
		return locations;
	}
		
	async print_location(){
		var self = this;
		var select_session = $('.select_session_id').val();
		var location = $('.summery_location_id').val();
		var order = self.pos.get_order();
		var summery_product = [];
		var tab1 = $('#tab1').is(':checked')
		var tab2 = $('#tab2').is(':checked')
		$('#select_ssn').hide();
		$('#select_loc').hide();
		var ram = false;
		if(tab1 == true)
		{
			ram = true;
			if(select_session){
				await self.orm.call(
					'pos.order.location',
					'update_location_summery',
					[location, location,select_session,tab1,tab2],
				).then(function(output_summery_location){
					var summery_loc = output_summery_location;
					self.save_location_summery_details(output_summery_location,ram);
				});
			}
			else{
				$('#select_ssn').show();
				setTimeout(function() {$('#select_ssn').hide()},3000);
				$('#tab1').prop('checked', true);
			}
		}
		else{
			if(location){
				await self.orm.call(
					'pos.order.location',
					'update_location_summery',
					[location, location,select_session,tab1,tab2],
				).then(function(output_summery_location){
					var summery_loc = output_summery_location;
					self.save_location_summery_details(output_summery_location,ram);
				
				});
			}
			else{
				$('#select_loc').show();
				setTimeout(function() {$('#select_loc').hide()},3000);
				$('#tab2').prop('checked', true);
			}
		}
	}
	
	save_location_summery_details(output_summery_location,ram){
		var self = this;
		this.props.close({ confirmed: false, payload: null });
		self.pos.showTempScreen('LocationReceiptScreen',{output_summery_location:output_summery_location,ssn:ram});
	}

}