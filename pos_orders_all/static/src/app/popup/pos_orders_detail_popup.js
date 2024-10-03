/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";

export class PosOrdersDetailPopup extends AbstractAwaitablePopup {
    static template = "pos_orders_all.PosOrdersDetailPopup";
    static defaultProps = {
        confirmText: _t("Ok"),
        cancelKey: false,
        body: "",
    };

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
        let a=dt.split(" ");            
        let a1=a[0]+'T';
        let a2=a[1]+'Z';
        let final_date=a1+a2;
        let date = new Date(final_date);
        let new_date = this.GetFormattedDate(date);
        return new_date
    }

    getPayload() {}
}
