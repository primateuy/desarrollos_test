/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { CreateCouponPopup } from "@pos_orders_all/app/popup/create_coupon_popup";
import { SelectExistingCouponPopup } from "@pos_orders_all/app/popup/select_existing_coupon_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";


export class CouponConfigPopup extends AbstractAwaitablePopup {
    static template = "pos_orders_all.CouponConfigPopup";
    static defaultProps = {
        confirmText: _t("Ok"),
        cancelKey: false,
        body: "",
    };

    setup() {
        super.setup();  
        this.pos = usePos();    
    }

    create_coupon(){
        var order = this.pos.get_order();
        if(order){
            var orderlines = order.get_orderlines();
            var self = this;
            if(order.get_is_coupon_used() == undefined){
                order.is_coupon_used = false;
            }
            self.cancel();
            this.pos.popup.add(CreateCouponPopup,{});
        }
    }

    select_coupon(){
        var order = this.pos.get_order();
        if(order){
            var orderlines = order.get_orderlines();
            var self = this;
            if(order.get_is_coupon_used() == undefined){
                order.is_coupon_used = false;
            }

            if(order.is_coupon_used == true){
                this.pos.popup.add(ErrorPopup,{
                    title: _t("Already Used !!!"),
                    body:_t("You have already use Coupon code, at a time you can use one coupon in a Single Order"),
                });
            }
            else if (order.get_partner() == null){
                this.pos.popup.add(ErrorPopup, {
                    title: _t('Unknown customer'),
                    body: _t('You cannot use Coupons/Gift Voucher. Select customer first.'),
                });
                return;
            }
            else if (orderlines.length === 0) {
                this.pos.popup.add(ErrorPopup, {
                    title: _t('Empty Order'),
                    body: _t('There must be at least one product in your order before it can be apply for voucher code.'),
                });
                return;
            }
            else{
                self.cancel();
                this.pos.popup.add(SelectExistingCouponPopup,{});
            }
        }
    }
}
