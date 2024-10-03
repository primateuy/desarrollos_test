/** @odoo-module */

import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { debounce } from "@web/core/utils/timing";
import { SaleOrdersLine } from "@pos_orders_all/app/screens/product_screen/sale_orders_screen/sale_orders_line";
import { useRef, useState, Component,onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class SaleOrderScreen extends Component {
    static components = { SaleOrdersLine };
    static template = "pos_orders_all.SaleOrderScreen";

    setup() {
        super.setup();
        this.pos = usePos();
        this.orm = useService("orm");
        this.state = useState({all_order_data : [] || false, all_order_data_line: [] || false, query: null, selectedSaleOrder: this.props.partner,});
        this.searchWordInputRef = useRef('search-word-input-partner');
        this.updateOrderList = debounce(this.updateOrderList, 70);
        onWillUnmount(this.updateOrderList.cancel);
    }

    back() {
         this.pos.showScreen("ProductScreen");
    }
    async searchSaleOrder() {
        var self = this;
        var ord_list = []
        if (this.state.previousQuery != this.state.query) {
            this.state.currentOffset = 0;
        }
        let result = await this.getNewSaleOrder();
        this.state.all_order_data.pop();
        result.forEach(function(ol) {

            ord_list.push(self.env.services.pos.db.get_so_by_id[ol])

        });
        self.state.all_order_data.push(ord_list)
        this.render(true);
        if (this.state.previousQuery == this.state.query) {
            if(result){
                this.state.currentOffset += result.length;
            }
        } else {
            this.state.previousQuery = this.state.query;
            if(result){
                this.state.currentOffset = result.length;
            }
        }
        return self.state.all_order_data;
    }

    async getNewSaleOrder() {
        var domain = [];
        const limit = 30;
        if(this.state.query) {
            domain = [["name", "ilike", this.state.query]];
            const result = await this.orm.silent.call(
                "sale.order",
                "search",
                [domain]
            );
            return result;

        }
    }

    refresh_orders(){
        this.get_all_order_data();
    }

    async _onPressEnterKey() {
        const result = await this.searchSaleOrder();
    }

    async updateOrderList(event) {
        this.state.query = event.target.value;
        if(!this.state.query){
            this.state.all_order_data.pop();
            this.get_all_order_data();
            this.render();
        } else{
            this._onPressEnterKey();
            this.render(true);
        }
    }

    async _clearSearch() {
        this.searchWordInputRef.el.value = "";
        this.state.query = "";
        this._onPressEnterKey();
        this.render(true);
    }

    clickSaleOrder(order) {
        if (this.state.selectedSaleOrder === order) {
            this.state.selectedSaleOrder = null;
        } else {
            this.state.selectedSaleOrder = order;
        }
        this.render();
    }

    async get_current_day() {
        let self = this;
        let days = self.pos.config.load_orders_days;
        let today = new Date();
        if(days > 0){
            today.setDate(today.getDate() - days);
        }
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

    async get_orders_domain(){
        let self = this;
        let pos_config = self.pos.config;
        let today = await self.get_current_day();
        let days = self.pos.config.load_orders_days;
        let is_draft_sent= pos_config.load_draft_sent;
        if(days > 0)
        {
            if(is_draft_sent){
                return [['date_order', '>=',today],['state','in',['draft','sent']]];
            }
            else{
                return [['date_order', '>=',today]];
            }
        }
        else{
            if(is_draft_sent){
                return [['state','in',['draft','sent']]];
            }else{
                return [['state','not in',['cancel']]];
            }
        }
    }

    async get_all_order_data () {
        let self = this;
        let sale_domain = await self.get_orders_domain();

        let load_orders = [];
        let load_orders_line = [];
        let order_ids = [];
        try {
            await self.env.services.orm.call("sale.order", "search_read", [sale_domain]).then(function(output) {
                load_orders = output;
                self.env.services.pos.db.get_so_by_id = {};
                load_orders.forEach(function(order) {
                    order_ids.push(order.id)
                    self.env.services.pos.db.get_so_by_id[order.id] = order;
                });
                let fields_domain = [['order_id','in',order_ids]];

                self.env.services.orm.call("sale.order.line", "search_read", [fields_domain]).then(function(output1) {
                    load_orders_line = output1;

                    self.saleorders = load_orders;
                    self.so_lines = output1;
                    self.env.services.pos.db.get_so_line_by_id = {};
                    output1.forEach(function(ol) {
                        self.env.services.pos.db.get_so_line_by_id[ol.id] = ol;
                    });
                });
            });
            if(this.state.all_order_data.length == 0){
                this.state.all_order_data.push(load_orders)
            }
        }catch (error) {
            if (error.message.code < 0) {

                await this.pos.popup.add(SaleCreatePopup,{
                    title: _t("Offline"),
                    body: _t( "Unable to load saleorders."),
                });
            } else {
                throw error;
            }
        }
    }

}

registry.category("pos_screens").add("SaleOrderScreen", SaleOrderScreen);