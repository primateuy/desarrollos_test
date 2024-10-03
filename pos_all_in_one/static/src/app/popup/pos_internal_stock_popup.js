/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { PosConfirmationPopup } from "@pos_all_in_one/app/popup/pos_confirmation_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";

export class PosInternalStockPopup extends AbstractAwaitablePopup {
    static template = "pos_all_in_one.PosInternalStockPopup";
    static defaultProps = {
        confirmText: _t("Create Transfer"),
        cancelText: _t("Close"),
        title: _t("Internal Stock Transfer"),
        body: "",
    };


    setup() {
        super.setup();
        this.pos = usePos();
        this.orm = useService("orm");
	}	

	create_transfer() {
		var self = this;

		var order = this.pos.get_order();
		var orderlines = order.get_orderlines();

		var picking_type = $('.drop-type').val();
		var src = $('.drop-src').val();
		var dest = $('.drop-dest').val();
		var state = $('.drop-state').val();
		if (order.get_partner()){
			var client = order.get_partner().id;
		}
		else{
			var client = false;
		}
		if(!picking_type || !src || !dest || !state){
			alert("Please select all options");
		}
		else if(parseInt(src) == parseInt(dest)){
			alert("You can not choose  same location as source location and destination location");
		}
		else{
			if(orderlines.length!=0){
				var product_ids = []
				for(var i=0;i<orderlines.length;i++){
					var prod_exist = $.grep(product_ids, function(v) {
						return v.product_id === orderlines[i].product.id;
					});
					if(prod_exist.length!=0){
						prod_exist[0]['quantity'] += orderlines[i].quantity
					}
					else{
						product_ids.push({
							'product_id': orderlines[i].product.id,
							'quantity': orderlines[i].quantity
						});
					}
				}

				this.orm.call(
					'pos.session',
					'checking_product',
					[1,product_ids],
				).then(function(output) {
					if(output[1].length!=0){
						var product;
						var name_product= '';
						for (var i = 0; i<output[1].length; i++)
						{
							product = self.env.pos.db.get_product_by_id(output[1][i])
							name_product += product.display_name+','
						}
						alert(name_product+"Product are serviceable so picking not generate for this products.")
					}
					if(output[0].length!=0){
						self.orm.call(
							'pos.session',
							'generate_internal_picking',
							[1,client,picking_type,src,dest,state,product_ids],
						).then(function(output) {
							if(output){
							    self.cancel();
							    self.pos.popup.add(PosConfirmationPopup, {
						            transfer_name: output.pick_name, transfer_id: output.pick_id
						        });
								product_ids = []
								self.remove_current_orderlines();
							}
						});
					}
				});
			}else{
				alert("Please Select Product first.")
			}
		}
	}

	cancel() {
        this.props.close({ confirmed: false, payload: null });
    }

    remove_current_orderlines(){
		let self = this;
		let order = self.pos.get_order();
		let orderlines = order.get_orderlines();
		order.set_partner(null);           
        while (orderlines.length > 0) {
            orderlines.forEach(function (line) {
                order.removeOrderline(line);
            });
        }
	}

}