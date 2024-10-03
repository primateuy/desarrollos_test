/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class SelectExistingCouponPopup extends AbstractAwaitablePopup {
    static template = "pos_orders_all.SelectExistingCouponPopup";

    setup() {
        super.setup();
        this.pos = usePos();
        this.orm = useService("orm");
    }
   async apply_coupon () {
        let self = this;
        let order = this.pos.get_order();
        if(order){
            let orderlines = order.get_orderlines();
            let selectedOrder = this.pos.get_order();
            let entered_code = $("#existing_coupon_code").val();
            let partner_id;
            let coupon_applied = true;
            let used = false;
            if (order.get_partner() != null){
                partner_id = order.get_partner();
            }
            let total_amount = selectedOrder.get_total_without_tax();

            await self.orm.call(
                'pos.gift.coupon',
                'search_coupon',
                [1, entered_code],

            ).then(function(output) {
                if(output.length > 0)
                {
                    let amount = output[1];
                    used = output[2];
                    let coupon_count = output[3];
                    let coupon_times = output[4];
                    let expiry = output[5];
                    let partner_true = output[6];
                    let gift_partner_id = output[7];
                    let amount_type = output[8]
                    let exp_dt_true = output[9];
                    let max_amount = output[10];
                    let apply_coupon_on = output[11];
                    let current_date = new Date().toUTCString();
                    let d = new Date();
                    let month = '0' + (d.getMonth() + 1);
                    let day = '0' + d.getDate();
                    let year = d.getFullYear();
                    let product_id = output[12];
                    let is_categ = output[13];
                    let categ_ids = output[14];
                    let categ_amount = 0.0;
                    let order_total = order.get_total_with_tax();
                    let categ_total = 0;
                    expiry = new Date(expiry)
                    let date = new Date(year,month,day);
                    if(amount_type == 'per'){
                        if(apply_coupon_on == 'taxed')
                        {
                            total_amount = order.get_total_with_tax();
                        }
                        amount = (total_amount * output[1])/100;
                    }else{
                        amount = amount;
                    }
                    if(categ_ids.length > 0 && is_categ){
                        orderlines.forEach(function (line) {
                            categ_ids.forEach(function (c_id) {
                                if(line.product.pos_categ_ids){
                                    line.product.pos_categ_ids.forEach(function (pos_catge_id) {

                                        if(pos_catge_id == c_id){
                                            if(amount_type == 'per'){
                                                if(apply_coupon_on == 'taxed'){
                                                    let tt =  parseFloat(line.get_tax() + line.get_display_price())
                                                    categ_amount += (tt * output[1])/100;
                                                }
                                                else{
                                                    categ_amount +=  (line.get_base_price() * output[1])/100;
                                                }
                                            }else{
                                                categ_amount =  output[1];
                                            }
                                            categ_total +=  parseFloat(line.get_tax() + line.get_display_price());
                                        }
                                    });
                                }
                            });
                        });
                        amount = categ_amount;
                        order_total = categ_total;
                    }

                    if (exp_dt_true && d > expiry){
                        self.pos.popup.add(ErrorPopup, {
                            title: _t('Expired'),
                            body: _t("The Coupon You are trying to apply is Expired"),
                        });
                    }
                    else if (coupon_count > coupon_times){ // maximum limit
                        self.pos.popup.add(ErrorPopup, {
                            title: _t('Maximum Limit Exceeded !!!'),
                            body: _t("You already exceed the maximum number of limit for this Coupon code"),
                        });
                    }

                    else if (partner_true == true && gift_partner_id != partner_id.id){
                        self.pos.popup.add(ErrorPopup, {
                            title: _t('Invalid Customer !!!'),
                            body: _t("This Gift Coupon is not applicable for this Customer"),
                        });
                    }
                    else if(order_total < amount){
                        self.pos.popup.add(ErrorPopup, {
                            title: _t('Invalid Amount !!!'),
                            body:_t("Coupon Amount is greater than order amount"),
                        });
                    }


                    else if(amount <= 0 ){
                        self.pos.popup.add(ErrorPopup, {
                            title: _t('Invalid Amount !!!'),
                            body:_t("Coupon is not applicable here."),
                        });
                    }
                    else {
                        if(max_amount >= amount){
                            let update_coupon_amount = max_amount - amount
                            order.coup_maxamount = update_coupon_amount;
                            let total_val = total_amount - amount;
                            let product = self.pos.db.get_product_by_id(product_id);
                            if(product == undefined){
                                self.pos.popup.add(ErrorPopup, {
                                    title: _t('Product Not Available !!!'),
                                    body: _t("Product Not available in POS."),
                                });
                            }else{
                                let selectedOrder = self.pos.get_order();
                                selectedOrder.add_product(product, {
                                    price: -amount,
                                    quantity: 1.0,
                                });
                                order.set_is_coupon_used(true);
                                order.get_selected_orderline().set_is_coupon_line(true)
                                order.coupon_id = output[0];
                                self.cancel();
                            }
                        }else if(max_amount == 0){
                            self.pos.popup.add(ErrorPopup, {
                                title: _t('Discount Limit Exceeded !!!'),
                                body: _t("Discount amount is higher than maximum amount of this coupon."),
                            });
                        }else if(max_amount <= amount){
                            var max = max_amount;
                            let update_coupon_amount = max_amount - max
                            order.coup_maxamount = update_coupon_amount;

                            let total_val = total_amount - max_amount;
                            let product = self.pos.db.get_product_by_id(product_id);
                            if(product == undefined){
                                self.pos.popup.add(ErrorPopup, {
                                    title: _t('Product Not Available !!!'),
                                    body: _t("Product Not available in POS."),
                                });
                            }else{
                                let selectedOrder = self.pos.get_order();
                                selectedOrder.add_product(product, {
                                    price: -max_amount,
                                    quantity: 1.0,
                                });
                                order.set_is_coupon_used(true);
                                order.coupon_id = output[0];
                                self.cancel();
                            }
                        }
                    }
                }else { //Invalid Coupon Code
                    self.pos.popup.add(ErrorPopup, {
                        title: _t('Invalid Code !!!'),
                        body: _t("Voucher Code Entered by you is Invalid. Enter Valid Code..."),
                    });
                }
            });
        }
    }
}