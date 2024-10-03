/** @odoo-module */

import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, onMounted } from "@odoo/owl";

export class CouponPrint extends Component {
    static template = "pos_orders_all.CouponPrint";
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        var self = this;
		var order = this.pos.get_order();
		var number_bar = this.props.data.coup_code;

		onMounted(() => {
			$("#barcode_print2").barcode(
				number_bar, // Value barcode (dependent on the type of barcode)
				"code128" // type (string)
			);
        });
    }

    coupon_render_env() {
		var data= this.props.data;
		var vals = {
			widget: this,
			pos: this.env.pos,
			name: data.coup_name,
			issue: data.coup_issue_dt,
			expire : data.coup_exp_dt,
			amount : data.coup_amount,
			number : data.coup_code,
			am_type : data.am_type,
		}
		return vals;
	}  
}

registry.category("pos_screens").add("CouponPrint", CouponPrint);


