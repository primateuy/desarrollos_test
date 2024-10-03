/** @odoo-module **/

    import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
    import { usePos } from "@point_of_sale/app/store/pos_hook";
    import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
    import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
    let redeem
    let loyalty_settings
    
    export class LoyaltyPopupWidget extends AbstractAwaitablePopup {
        static template = "pos_all_in_one.LoyaltyPopupWidget";
        static components = { ProductCard };

        setup() {
            super.setup();
            this.pos = usePos();
            this.calculate_loyalty_points();
        }

    	calculate_loyalty_points(){
			let self = this;
			let order = this.pos.get_order();
			let orderlines = order.get_orderlines();
			let partner = this.props.partner;
			loyalty_settings = this.pos.pos_loyalty_setting;
			
			self.partner = partner || {};
			self.loyalty = partner.loyalty_points1;
			if(loyalty_settings.length != 0){
				let product_id = loyalty_settings[0].product_id[0];
				let product = this.pos.db.get_product_by_id(product_id);
				self.product = product;
				if(loyalty_settings[0].redeem_ids.length != 0){
					let redeem_arr = []
					for (let i = 0; i < loyalty_settings[0].redeem_ids.length; i++) {
						for (let j = 0; j < this.pos.pos_redeem_rule.length; j++) {
							if(loyalty_settings[0].redeem_ids[i] == this.pos.pos_redeem_rule[j].id)
							{
								redeem_arr.push(this.pos.pos_redeem_rule[j]);
							}
						}
					}
					for (let j = 0; j < redeem_arr.length; j++) {
						if( redeem_arr[j].min_amt <= partner.loyalty_points1 && partner.loyalty_points1 <= redeem_arr[j].max_amt)
						{
							redeem = redeem_arr[j];
							break;
						}
					}
					if(redeem){
						let point_value = redeem.reward_amt * self.loyalty;
						if (partner){
							self.loyalty_amount = point_value;
							partner.loyalty_amount = point_value;
						}
					}
				}
			}
		}

		redeemPoints() {
			let self = this;
			let order = this.pos.get_order();
			let orderlines = order.get_orderlines();
			let entered_code = $("#entered_item_qty").val();
			let point_value = 0;
			let remove_line;	
			let partner = this.props.partner;
			let loyalty = partner.loyalty_points1;
            loyalty_settings = this.pos.pos_loyalty_setting;

			if(entered_code<0)
			{
				alert('Please enter valid amount.');
				return
			}
			if(redeem && redeem.min_amt <= loyalty &&  loyalty<= redeem.max_amt)
			{
				if(entered_code <= loyalty)
				{
					let total = order.get_total_with_tax();
					let redeem_value = redeem.reward_amt * entered_code
					if (redeem_value > total) {
						alert('Please enter valid amountss.')
					}
					if (redeem_value <= total) {
                        order.add_product(self.product, {
							price: -redeem_value
						});

						var last_line = order.get_last_orderline()
						last_line.set_cust_redeem_line(true)
						partner.loyalty_points1 -= entered_code;
						remove_line = orderlines[orderlines.length-1].id
						order.redeemed_points = entered_code;
						order.redeem_done = true;
						order.redeem_point = entered_code;
						order.remove_line = remove_line;
						self.cancel();
					}
				}
				else{
					alert('Please enter valid amount.');
				}
			}
			else{
				alert("limit exceeded");
			}	
					  
		}
    }