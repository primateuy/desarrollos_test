/** @odoo-module **/

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { _t } from "@web/core/l10n/translation";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { LoyaltyPopupWidget } from "@pos_all_in_one/app/popup/loyalty_popup_widget";


export class LoyaltyButton extends Component {
    static template = "pos_all_in_one.LoyaltyButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }
    
    async click() {
        let self = this;

        let order = this.pos.get_order();
		let partner = false;
		let loyalty_points = 0;
		if(order.orderlines.length>0){
			if(this.pos.pos_loyalty_setting.length != 0){
				if (order.get_partner() != null){
					partner = order.get_partner();
					loyalty_points = partner.loyalty_points1;
				}
				if(order.getHasRedeemLine()){
					this.popup.add(ErrorPopup, {
	                    title: _t("Redeem Product"),
	                    body: _t("Sorry, you already added the redeem product."),
	                });
	                return;
				}
				else if(this.pos.pos_loyalty_setting[0].redeem_ids.length == 0)
				{	
					this.popup.add(ErrorPopup, {
	                    title: _t("No Redemption Rule"),
	                    body: _t("Please add Redemption Rule in loyalty configuration"),
	                });
	                return;
				}
				else if(!partner){

					this.popup.add(ErrorPopup, {
	                    title: _t("Unknown customer"),
	                    body: _t("You cannot redeem loyalty points. Select customer first."),
	                });
	                return;
				}
				else if(loyalty_points < 1){

					this.popup.add(ErrorPopup, {
	                    title: _t("Insufficient Points"),
	                    body: _t("Sorry, you do not have sufficient loyalty points."),
	                });
	                return;
				}
				else{
					this.popup.add(LoyaltyPopupWidget, {'partner': partner});
				} 
			}    
		}
		else{
			this.popup.add(ErrorPopup, {
                title: _t("Empty Order"),
                body: _t("Please select some products"),
            });
            return;
		}
    }
}

ProductScreen.addControlButton({
    component: LoyaltyButton,
    condition: function () {
        if(this.pos.pos_loyalty_setting.length > 0){
			return true;
		}else{
			return false;
		}
    },
});