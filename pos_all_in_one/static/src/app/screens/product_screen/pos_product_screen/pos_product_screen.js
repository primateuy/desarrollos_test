/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";

import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component, useState } from "@odoo/owl";
import { groupBy } from "@web/core/utils/arrays";
const { onMounted, onPatched, useRef } = owl;
import { debounce } from "@bus/workers/websocket_worker_utils";
import { POSProduct } from "@pos_all_in_one/app/screens/product_screen/pos_product_screen/pos_product";
import { ProductDetailsCreatePopup } from "@pos_all_in_one/app/popup/product_details_create_popup";
import { PosProductDetailPopup } from "@pos_all_in_one/app/popup/pos_product_detail_popup";

export class PosProductScreen extends Component {
    static template = "pos_all_in_one.PosProductScreen";
    static components = { POSProduct };

    setup() {
        super.setup();
        var self = this;
        this.pos = usePos();
        this.state = {
            query: null,
            selectedPosOrder: this.props.client,
        };
        this.searchWordInputRef = useRef('search-word-input-partner');
        // useListener('click-showDetails', this.showDetails);
        let pd = this.prod_data;
    }

    back() {
        this.props.resolve({ confirmed: false, payload: false });
        this.pos.closeTempScreen();
    }

    get prod_data(){
        let product_dict = this.pos.db.product_by_id;
        let data = [];
        $.each( product_dict, function( key, value ) {
            if(key != 'undefined' ){
                data.push(value)
            }
        });
        this.updateProductList = debounce(this.updateProductList, 70);
        this.orders = data || [];
    }

    get currentOrder() {
        return this.env.pos.get_order();
    }

    get pos_products() {
        let self = this;
        let query = this.state.query;
        if(query){
            query = query.trim();
            query = query.toLowerCase();
        }
        if (query && query !== '') {
            return this.search_orders(this.orders,query);
        } else {
            return this.orders;
        }
    }

    _clearSearch() {
        this.searchWordInputRef.el.value = '';
        this.state.query = '';
        this.state.searchWord = '';
        this.render(true);
    }

    search_orders(orders,query){
        let self = this;
        let selected_orders = [];
        let search_text = query;            
        orders.forEach(function(odr) {
            if (search_text) {
                if (((odr.display_name.toLowerCase()).indexOf(search_text) != -1)) {
                    selected_orders.push(odr);
                }
                else if(odr.barcode != false){
                    if(odr.barcode.indexOf(search_text) != -1){
                        selected_orders.push(odr);
                    }
                }
                else if(odr.default_code != false){
                    if (((odr.default_code.toLowerCase()).indexOf(search_text) != -1)) {
                        selected_orders.push(odr);
                    }
                }
            }
        });
        return selected_orders;
    }

    refresh_orders(){
        let self = this;
        let pd = this.prod_data;
        this.state.query = '';
        this.searchWordInputRef.el.value = '';
        this.render();
        this.render();
        this.render();
    }

    create_order(event){
        this.pos.popup.add(ProductDetailsCreatePopup, {
            products : {values: null}
        })
    }

    updateProductList(event) {
        this.state.query = event.target.value;
        const pos_products = this.pos_products;
        if (event.code === 'Enter' && pos_products.length === 1) {
            this.state.selectedPosOrder = pos_products[0];
        } else {
            this.render();
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

    showDetails(order){
        let self = this;
        self.pos.popup.add(PosProductDetailPopup, {
            'order': order, 
        });
    }

}

registry.category("pos_screens").add("PosProductScreen", PosProductScreen);
