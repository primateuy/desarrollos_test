/** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { debounce } from "@web/core/utils/timing";
import { useService } from "@web/core/utils/hooks";
import { useAsyncLockedMethod } from "@point_of_sale/app/utils/hooks";
import { session } from "@web/session";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, onWillUnmount, useRef, useState } from "@odoo/owl";
import { PosOrdersLine } from "@pos_orders_all/app/screens/product_screen/pos_orders_screen/pos_orders_line";
import { PosOrdersDetailPopup } from "@pos_orders_all/app/popup/pos_orders_detail_popup";
import { ReOrderPopup } from "@pos_orders_all/app/popup/reorder_popup";
import { ReturnOrderPopup } from "@pos_orders_all/app/popup/return_order_popup";


export class PosOrdersScreen extends Component {
    static components = { PosOrdersLine };
    static template = "pos_orders_all.PosOrdersScreen";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
        this.orm = useService("orm");
        this.state = useState({
            query: null,
            selectedPosOrder: this.props.partner,
        });
        this.searchWordInput = useRef('search-word-input-pos-order');
        this.orders = this.get_pos_orders()[0] || [];
        this.orderlines = this.get_pos_orders()[1] || [];
        this.updateOrderList = debounce(this.updateOrderList, 70);
    }

    back() {
        this.pos.showScreen("ProductScreen");
    }

    refresh_orders(){
        $('.input-search-orders').val('');
        this.state.query = '';
        this.props.selected_partner_id = false;
        this.render();
    }

    updateOrderList(event) {
        this.state.query = event.target.value;
        const pos_orders = this.pos_orders;
        if (event.code === 'Enter' && pos_orders.length === 1) {
            this.state.selectedPosOrder = pos_orders[0];
        } else {
            this.render();
        }
    }

    _onSelectState(ev){
        this.updateOrderList(ev)
    }

    async _clearSearch() {
        this.searchWordInput.el.value = "";
        this.state.query = "";
        this.render(true);
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

    get_orders_domain(){
        let self = this; 
        let current = self.pos.pos_session.id;
        let pos_config = self.pos.config;
        let today = self.get_current_day();

        if (pos_config.pos_session_limit == 'all')
        {
            if(pos_config.show_draft == true)
            {
                if(pos_config.show_posted == true)
                {
                    return [['state', 'in', ['draft','done']]]; 
                }
                else{
                    return [['state', 'in', ['draft']]]; 
                }
            }
            else if(pos_config.show_posted == true)
            {
                return [['state', 'in', ['done']]];
            }
            else{
                return [['state', 'in', ['draft','done','paid','invoiced','cancel']]]; 
            }   
        }
        else if (pos_config.pos_session_limit == 'last3')
        {
            if(pos_config.show_draft == true)
            {
                if(pos_config.show_posted == true)
                {
                    return [['state', 'in', ['draft','done']],['session_id', 'in',[current,current-1,current-2,current-3]]]; 
                }
                else{
                    return [['state', 'in', ['draft']],['session_id', 'in',[current,current-1,current-2,current-3]]]; 
                }
            }
            else if(pos_config.show_posted == true)
            {
                return [['state', 'in', ['done']],['session_id', 'in',[current,current-1,current-2,current-3]]];
            }
            else{
                return [['session_id', 'in',[current,current-1,current-2,current-3]]]; 
            }
        }
        else if (pos_config.pos_session_limit == 'last5')
        {
            if(pos_config.show_draft == true)
            {
                if(pos_config.show_posted == true)
                {
                    return [['state', 'in', ['draft','done']],['session_id', 'in',[current,current-1,current-2,current-3,current-4,current-5]]]; 
                }
                else{
                    return [['state', 'in', ['draft']],['session_id', 'in',[current,current-1,current-2,current-3,current-4,current-5]]]; 
                }
            }
            else if(pos_config.show_posted == true)
            {
                return [['state', 'in', ['done']],['session_id', 'in',[current,current-1,current-2,current-3,current-4,current-5]]];
            }
            else{
                return [['session_id', 'in',[current,current-1,current-2,current-3,current-4,current-5]]]; 
            }
        }
        
        else if (pos_config.pos_session_limit == 'current_session')
        {
            if(pos_config.show_draft == true)
            {
                if(pos_config.show_posted == true)
                {
                    return [['state', 'in', ['draft','done']],['session_id', 'in',[current]]]; 
                }
                else{
                    return [['state', 'in', ['draft']],['session_id', 'in',[current]]]; 
                }
            }
            else if(pos_config.show_posted == true)
            {
                return [['state', 'in', ['done']],['session_id', 'in',[current]]];
            }
            else{
                return [['session_id', 'in',[current]]]; 
            }
        }
        else if (self.pos.config.pos_session_limit == 'current_day')
        {
            let today = self.get_current_day();

            if(pos_config.show_draft == true)
            {
                if(pos_config.show_posted == true)
                {
                    return [['state', 'in', ['draft','done']],['date_order', '>=', today + ' 00:00:00'],['date_order', '<=', today + ' 23:59:59']];
                }
                else{
                    return [['state', 'in', ['draft']],['date_order', '>=', today + ' 00:00:00'],['date_order', '<=', today + ' 23:59:59']];
                }
            }
            else if(pos_config.show_posted == true)
            {
                return [['state', 'in', ['done']],['date_order', '>=', today + ' 00:00:00'],['date_order', '<=', today + ' 23:59:59']];
            }
            else{
                return [['date_order', '>=', today + ' 00:00:00'],['date_order', '<=', today + ' 23:59:59']];
            }
        }
        else{
            return [];
        }
    }

    async get_pos_orders () {
        let self = this;
        let domain = self.get_orders_domain();
        var fields = ['name','date_order','user_id','amount_tax','amount_total','amount_paid','amount_return',
                        'lines','company_id','pricelist_id','partner_id','sequence_number','session_id',
                        'config_id','currency_id','state','account_move','picking_ids',
                        'picking_type_id','procurement_group_id','note','nb_print','pos_reference',
                        'sale_journal','fiscal_position_id','payment_ids','session_move_id','to_invoice',
                        'is_invoiced','is_tipped','tip_amount','is_refunded','refunded_order_ids',
                        'has_refundable_lines','refunded_orders_count'];
        let load_orders = [];
        let load_orders_line = [];
        let order_ids = [];
        try {
            await this.orm.call(
                "pos.order",
                "search_read",
                [],
                {domain,fields},
                ).then(function(output) {
                    load_orders = output;
                    self.pos.db.get_orders_by_id = {};
                    self.pos.db.get_orders_by_barcode = {};
                    load_orders.forEach(function(order) {
                        order_ids.push(order.id)
                        self.pos.db.get_orders_by_id[order.id] = order;     
                        self.pos.db.get_orders_by_barcode[order.barcode] = order;                       
                    });

                    self.orm.call(
                        "pos.order.line",
                        "search_read",
                        [[['order_id','in',order_ids]]],
                        ).then(function(output1) {
                            self.pos.db.all_orders_line_list = output1;
                            load_orders_line = output1;

                            self.pos.synch.all_orders_list = load_orders
                            self.pos.synch.all_orders_line_list = output1

                            self.orders = load_orders;
                            self.orderlines = output1;

                            self.pos.db.get_orderline_by_id = {};
                            output1.forEach(function(ol) {
                                self.pos.db.get_orderline_by_id[ol.id] = ol;                        
                            });

                            self.render();
                            return [load_orders,load_orders_line]
                        }
                    )                    
                }
            ); 
        }catch (error) {
            if (error.message.code < 0) {
                await this.popup.add('OfflineErrorPopup', {
                    title: _t('Offline'),
                    body: _t('Unable to load orders.'),
                });
            } else {
                throw error;
            }
        }
    }

    get pos_orders() {
        let self = this;
        let query = this.state.query;
        if(query){
            query = query.trim();
            query = query.toLowerCase();
        }
        if(this.orders){
            if ((query && query !== '') || 
                (this.props.selected_partner_id)) {
                return this.search_orders(this.orders,query);
            } else {
                return this.orders;
            }
        }
        else{
            let odrs = this.get_pos_orders()[0] || [];
            if (query && query !== '') {
                return this.search_orders(odrs,query);
            } else {
                return odrs;
            }
        }
    }

    clickPosOrder(order) {
        if (this.state.selectedPosOrder === order) {
            this.state.selectedPosOrder = null;
        } else {
            this.state.selectedPosOrder = order;
        }
        this.showDetails(order)
        this.render();
    }

    async showDetails(order){
        let self = this;
        let o_id = parseInt(order.id);
        let orders =  self.orders;
        let orderlines =  self.orderlines;
        let orders1 = [event.detail];
        
        let pos_lines = [];

        for(let n=0; n < orderlines.length; n++){
            if (orderlines[n]['order_id'][0] ==o_id){
                pos_lines.push(orderlines[n])
            }
        }
        await this.popup.add(PosOrdersDetailPopup, { 'order': order,'orderline':pos_lines, });
    }

    search_orders(orders,query){
        var self = this;
        let selected_orders = [];
        if (query == 'all_orders'){
            orders.forEach(function(odr) {
                selected_orders.push(odr);
            });
        }
        let search_text = query;
        let selected_partner = self.props.selected_partner_id;
        orders.forEach(function(odr) {
            if ((odr.partner_id == '' || !odr.partner_id) && search_text) {
                if (((odr.name.toLowerCase()).indexOf(search_text) != -1) || 
                    ((odr.state.toLowerCase()).indexOf(search_text) != -1)||
                    ((odr.date_order).indexOf(search_text) != -1)||
                    ((odr.pos_reference.toLowerCase()).indexOf(search_text) != -1)) {
                    selected_orders.push(odr);
                }
            }
            else
            {
                if(search_text){
                    if (((odr.name.toLowerCase()).indexOf(search_text) != -1) || 
                        ((odr.state.toLowerCase()).indexOf(search_text) != -1)||
                        ((odr.date_order).indexOf(search_text) != -1)||
                        ((odr.pos_reference.toLowerCase()).indexOf(search_text) != -1)|| 
                        ((odr.partner_id[1].toLowerCase()).indexOf(search_text) != -1)) {
                        selected_orders.push(odr);
                    }
                }
                
                if(selected_partner){
                    if (odr.partner_id[0] == selected_partner){
                        selected_orders.push(odr);
                    }
                }
            }
        });
        if (selected_orders.length > 0){
            return selected_orders;
        }else{
            selected_orders = [];
            return selected_orders;
        }
    }

    async clickReOrder(order){
        let self = this;
        let o_id = parseInt(order.id);
        let orderlines =  self.orderlines;              
        let pos_lines = [];

        for(let n=0; n < orderlines.length; n++){
            if (orderlines[n]['order_id'][0] ==o_id){
                pos_lines.push(orderlines[n])
            }
        }

        await this.popup.add(ReOrderPopup, { 'order': order,'orderlines':pos_lines, });
    }

    async clickReturnOrder(order){
        let self = this;
        let o_id = parseInt(order.id);
        let orderlines =  self.orderlines;              
        let pos_lines = [];
        for(let n=0; n < orderlines.length; n++){
            if (orderlines[n]['order_id'][0] ==o_id){
                pos_lines.push(orderlines[n])
            }
        }
        
        await this.popup.add(ReturnOrderPopup, { 'order': order,'orderlines':pos_lines, });
    }

    async clickReprint(order){
        let self = this;
        await this.orm.call(
            "pos.order",
            "print_pos_receipt",
            [[order.id]],
            ).then(function(output) {
                let data = output;
                data['order'] = order;
                self.pos.showScreen('OrderReprintScreen',data);
            }
        );
    }

}

registry.category("pos_screens").add("PosOrdersScreen", PosOrdersScreen);
