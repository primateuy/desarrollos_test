/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { PosDB } from "@point_of_sale/app/store/db";
import { unaccent } from "@web/core/utils/strings";
import { patch } from "@web/core/utils/patch";


patch(PosDB.prototype, {

    get_invoices_sorted: function(max_count){
        max_count = max_count ? Math.min(this.invoice_sorted.length, max_count) : this.invoice_sorted.length;
        var invoice = [];
        for (var i = 0; i < max_count; i++) {
            invoices.push(this.invoice_by_id[this.invoice_sorted[i]]);
        }
        return invoices;
    },
                
    get_product_write_date:function(products){
        return this.invoice_write_date || "1970-01-01 00:00:00";
    },

    add_product_templates(product_templates){
        for(var temp=0 ; temp < product_templates.length; temp++){
            var product_template_attribute_value_ids = [];

            var prod_temp =  product_templates[temp] ; 
            this.product_template_by_id[prod_temp.id] = prod_temp;
            this.product_tmpl_id.push(prod_temp)
            for (var prod = 0; prod <prod_temp.product_variant_ids.length; prod++){
                var product = this.product_by_id[prod_temp.product_variant_ids[prod]]
                if(product_template_attribute_value_ids.length>0){
                    for (var i = 0; i < product.product_template_attribute_value_ids.length; i++){
                    product_template_attribute_value_ids.push(product.product_template_attribute_value_ids[i]);
                }
                product.template_name = prod_temp.name
                product.product_variant_count = prod_temp.product_variant_count;
                }

                
            }
            const unique_attribute_value_ids = [...new Set(product_template_attribute_value_ids)]
            this.product_template_by_id[prod_temp.id].product_template_attribute_value_ids = unique_attribute_value_ids;
        }
    },

    get_product_by_category_variants(category_id){
        var product_ids  = this.product_by_category_id[category_id];
        var list = [];
        var temp = this.product_tmpl_id;
        var product_tmpl_lst = []
        if (product_ids) {
            for (var i = 0; i < temp.length; i++) {
                for (var j = 0 ; j < product_ids.length ; j++){
                    var prd_prod = this.product_by_id[product_ids[j]]
                    if(jQuery.inArray( prd_prod.product_tmpl_id, product_tmpl_lst ) == -1){
                        if(prd_prod.product_tmpl_id == temp[i].id){
                            var prd_list = temp[i].product_variant_ids.sort();
                            list.push(prd_prod)
                            product_tmpl_lst.push(temp[i].id)
                        }
                    }
                }
            }
        }
        return list;
    },

    /* returns a list of products with :
     * - a category that is or is a child of category_id,
     * - a name, package or barcode containing the query (case insensitive) 
     */
    search_product_in_category(category_id, query){
        try {
            query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
            query = query.replace(/ /g,'.+');
            var re = RegExp("([0-9]+):.*?"+ unaccent(query),"gi");
        }catch(e){
            return [];
        }
        var results = [];
        var product_tmpl_lst = []
        var temp = this.product_tmpl_id;

        for(var i = 0; i < this.limit; i++){
            var r = re.exec(this.category_search_string[category_id]);
            if(r){
                var id = Number(r[1]);
                var prod  = this.get_product_by_id(id)
                for(var j = 0; j < temp.length ; j++){
                    if(jQuery.inArray( prod.product_tmpl_id, product_tmpl_lst ) == -1){
                        if(prod.product_tmpl_id == temp[j].id){
                            var prd_list = temp[i].product_variant_ids.sort();
                            results.push(prod)
                            product_tmpl_lst.push(temp[j].id)
                        }
                    }
                }
            }else{
                break;
            }
        }
        return results;
    },

    get_unpaid_orders: function(){
        var saved = this.load('unpaid_orders',[]);
        var orders = [];
        for (var i = 0; i < saved.length; i++) {
            let odr = saved[i].data;
            if(!odr.is_paying_partial && !odr.is_partial && !odr.is_draft_order){
                orders.push(saved[i].data);
            }
            if(odr.is_paying_partial || odr.is_partial || odr.is_draft_order){
                saved = saved.filter(o => o.id !== odr.uid);
            }
        }
        this.save('unpaid_orders',saved);
        return orders;
    },
});
        
