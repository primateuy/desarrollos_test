/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { useAsyncLockedMethod } from "@point_of_sale/app/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component} from "@odoo/owl";

export class PosOrdersLine extends Component {
    static template = "pos_orders_all.PosOrdersLine";

    setup() {
        this.pos = usePos();
    }

    get highlight() {
        return this.props.order !== this.props.selectedPosOrder ? '' : 'highlight';
    }

    GetFormattedDate(date) {
        var month = ("0" + (date.getMonth() + 1)).slice(-2);
        var day  = ("0" + (date.getDate())).slice(-2);
        var year = date.getFullYear();
        var hour =  ("0" + (date.getHours())).slice(-2);
        var min =  ("0" + (date.getMinutes())).slice(-2);
        var seg = ("0" + (date.getSeconds())).slice(-2);
        return year + "-" + month + "-" + day + " " + hour + ":" +  min + ":" + seg;
    }

    get_order_date(dt){
        /*dt +=' UTC' */
        let a=dt.split(" ");            
        let a1=a[0]+'T';
        let a2=a[1]+'Z';
        let final_date=a1+a2;
        let date = new Date(final_date);
        let new_date = this.GetFormattedDate(date);
        return new_date
    }
}

registry.category("pos_screens").add("PosOrdersLine", PosOrdersLine);
