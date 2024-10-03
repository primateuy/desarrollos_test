/** @odoo-module **/

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { ReturnOrderPopup } from "@pos_orders_all/app/popup/return_order_popup";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";


export class ReturnOrderButton extends Component {
    static template = "pos_orders_all.ReturnOrderButton";

    setup() {
        this.pos = usePos();
        this.orm = useService("orm");
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

    get_current_day() {
        let today = new Date();
        let dd = today.getDate();
        let mm = today.getMonth()+1; //January is 0!
        let yyyy = today.getFullYear();
        if(dd<10){
            dd='0'+dd;
        } 
        if(mm<10){
            mm='0'+mm;
        } 
        today = yyyy+'-'+mm+'-'+dd;
        return today;
    }
    
    async click() {
        let self = this;
        const PosOrder = this.pos.get_order();
        let load_orders = [];
        let load_orders_line = [];
        let order_ids = [];

        const pos_domain =PosOrder.get_orders_domain ||[];
        await self.orm.call(
            'pos.order',
            'search_read',
            [pos_domain],
        ).then(function(output) {
            if (self.pos.config.pos_session_limit == 'current_day')
            {
                let today = self.get_current_day();
                output.forEach(function(i) {
                    if(i.date_order >= today + ' 00:00:00' && i.date_order <= today + ' 23:59:59')
                    {
                        load_orders.push(i);
                    }
                });
            }
            else{
                load_orders = output;
            }
            self.pos.db.get_orders_by_id = {};
            self.pos.db.get_orders_by_barcode = {};
            load_orders.forEach(function(order) {
                order_ids.push(order.id)
                self.pos.db.get_orders_by_id[order.id] = order;     
                self.pos.db.get_orders_by_barcode[order.barcode] = order;                       
            });

            
            let fields_domain = [['order_id','in',order_ids]];
            self.orm.call(
                'pos.order.line',
                'search_read',
                [fields_domain],
            ).then(function(output1) {
                self.pos.db.all_orders_line_list = output1;
                load_orders_line = output1;

                self.pos.synch.all_orders_list = load_orders
                self.pos.synch.all_orders_list = output1                    
                self.orders = load_orders;
                self.orderlines = output1;

                self.pos.db.get_orderline_by_id = {};
                output1.forEach(function(ol) {
                    self.pos.db.get_orderline_by_id[ol.id] = ol;                        
                });
                return [load_orders,load_orders_line]
            });
        }); 


        const { confirmed, payload: inputNote } = await this.pos.popup.add(TextInputPopup, {
            title: _t('Return Order Barcode'),
        });

        if (confirmed) {
            let entered_barcode = inputNote;
            
            let order = self.pos.db.get_orders_by_barcode[entered_barcode];
            if(order){
                let orderlines = [];
                $.each(order.lines, function(index, value) {
                    let ol = self.pos.db.get_orderline_by_id[value];
                    orderlines.push(ol);
                });
                self.pos.popup.add(ReturnOrderPopup, {
                    'order': order, 
                    'orderlines':orderlines,
                });
            }else{
                self.pos.popup.add(ErrorPopup, {
                    'title': _t('Invalid Barcode'),
                    'body': _t("No Order Found for this Barcode"),
                });
            }
        }
    }
}

ProductScreen.addControlButton({
    component: ReturnOrderButton,
    condition: function () {
        return this.pos.config.show_order;
    },
});
