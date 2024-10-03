/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class AfterCreateCouponPopup extends AbstractAwaitablePopup {
    static template = "pos_orders_all.AfterCreateCouponPopup";

    setup() {
        super.setup();
        this.pos = usePos();
        this.render_coupon()
    }
    print_gift_coupon(ev) {
        let self = this;
        self.cancel();
        self.pos.showTempScreen('CouponReceiptScreen',{'data' : this.coupon_data});
    }

    render_coupon() {
        let self = this;
        let partner_id = false;
        let order = this.pos.get_order();
        if(order){
            let coupon_datails = false;
            if (order.get_partner() != null){
                partner_id = order.get_partner();
            }
            coupon_datails =  this.props.output;
            let coup_id = coupon_datails[0];
            let coup_name = coupon_datails[1];
            let coup_exp_dt = false;
            if(coupon_datails[2])
            {
                coup_exp_dt = coupon_datails[2].split(" ")[0];
            }
            let coup_issue_dt = coupon_datails[4];
            coup_issue_dt = coup_issue_dt.split(" ")[0];

            let coup_amount = coupon_datails[3];
            let coup_img = coupon_datails[7];
            let am_type = coupon_datails[6];
            let coup_code = coupon_datails[5];

            let coup_dict = {coup_id,coup_name,coup_exp_dt,coup_issue_dt,coup_amount,coup_img,am_type,coup_code}
            if(coup_dict){
                this.coupon_data = coup_dict
            }
        }
    }
}
