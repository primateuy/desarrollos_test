/** @odoo-module **/

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { CouponConfigPopup } from "@pos_orders_all/app/popup/coupon_config_popup";


export class GiftCouponButton extends Component {
    static template = "pos_orders_all.GiftCouponButton";

    setup() {
        this.pos = usePos();
    }

    async click() {
        await this.pos.popup.add(CouponConfigPopup,{});
    }
}

ProductScreen.addControlButton({
    component: GiftCouponButton,
    condition: function () {
        return true;
    },
});
