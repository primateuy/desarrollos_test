/** @odoo-module */
import { Order,Orderline } from "@point_of_sale/app/store/models";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { roundPrecision as round_pr, floatIsZero } from "@web/core/utils/numbers";
import { parseFloat as oParseFloat } from "@web/views/fields/parsers";


patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
        this.custom_stock_locations = loadedData['stock.location'] || [];
        this.pos_order = loadedData['pos_order'] || [];
        this.pos_gift_coupon = loadedData['pos.gift.coupon'] || [];
    },

    async addProductToCurrentOrder(product, options = {}) {
        let self = this;
        let pos_config = self.config;
        let allow_order = pos_config.pos_allow_order;
        let deny_order= pos_config.pos_deny_order || 0;
        let call_super = true;

        if(pos_config.display_stock && product.type == 'product'){
            if (allow_order == false){
                if (pos_config.pos_stock_type == 'onhand'){
                    if ( product.bi_on_hand <= 0 ){
                        call_super = false;
                        self.popup.add(ErrorPopup, {
                            title: _t('Deny Order'),
                            body: _t("Deny Order" + "(" + product.display_name + ")" + " is Out of Stock."),
                        });
                    }
                }
                if (pos_config.pos_stock_type == 'available'){
                    if ( product.bi_available <= 0 ){
                        call_super = false;
                        self.popup.add(ErrorPopup, {
                            title: _t('Deny Order'),
                            body: _t("Deny Order" + "(" + product.display_name + ")" + " is Out of Stock."),
                        });
                    }
                }
            }else{
                if (pos_config.pos_stock_type == 'onhand'){
                    if ( product.bi_on_hand <= deny_order ){
                        call_super = false;
                        self.popup.add(ErrorPopup, {
                            title: _t('Deny Order'),
                            body: _t("Deny Order" + "(" + product.display_name + ")" + " is Out of Stock."),
                        });
                    }
                }
                if (pos_config.pos_stock_type == 'available'){
                    if ( product.bi_available <= deny_order ){
                        call_super = false;
                        self.popup.add(ErrorPopup, {
                            title: _t('Deny Order'),
                            body: _t("Deny Order" + "(" + product.display_name + ")" + " is Out of Stock."),
                        });
                    }
                }
            }
        }
        if(call_super){
            super.addProductToCurrentOrder(product, options = {});
        }
    }       
});

patch(Order.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.total_qty = this.total_qty || 0;
        this.barcode = this.barcode || "";
        this.return_order_ref = this.return_order_ref || false;
        this.imported_sales = this.imported_sales || [];
        this.discount_type = this.pos.config.discount_type;
        this.is_coupon_used = this.is_coupon_used || false;
        this.coupon_id = this.coupon_id || false;
        this.coup_maxamount = this.coup_maxamount || false;
        this.set_barcode();
    },

    set_is_coupon_used(is_coupon_used){
        this.is_coupon_used = is_coupon_used;
    },

    get_is_coupon_used(is_coupon_used){
        return this.is_coupon_used;
    },

    set_total_qty(total_qty){
        this.total_qty = total_qty;
    },

    get_total_qty(){
        return this.total_qty;
    },

    set_barcode(){
        var self = this;    
        var temp = Math.floor(100000000000+ Math.random() * 9000000000000)
        self.barcode =  temp.toString();
    },

    set_return_order_ref(return_order_ref) {
        this.return_order_ref = return_order_ref;
    },

    set_imported_sales(so){
        let sale = so.toString();
        if(!this.imported_sales.includes(sale))
            this.imported_sales += sale+',';
    },

    get_imported_sales(){
        return this.imported_sales;
    },

    product_total(){
        let order = this.pos.get_order();
        var orderlines = order.get_orderlines();
        return orderlines.length;
    },

    set_interval(interval){
        this.interval=interval;
    },

    set_orderline_options(orderline,options){
        super.set_orderline_options(...arguments);
        if(options.discount_type){
            orderline.discount_type = options.discount_type
            this.discount_type = this.pos.config.discount_type
        }
    },
    get_fixed_discount(){
        var total=0.0;
        var i;
        var orderlines = this.get_orderlines()
        for(i=0;i<orderlines.length;i++) 
        {   
            total = total + parseFloat(orderlines[i].discount);
        }
        return total
    },

    get_total_discount(){
        var self = this;
        return round_pr(this.orderlines.reduce((function(sum, orderLine) {
            if(orderLine.discount_type){
                if (orderLine.discount_type == "Percentage"){
                    sum += parseFloat(orderLine.get_unit_price() * (orderLine.get_discount()/100) * orderLine.get_quantity());
                    if (orderLine.display_discount_policy() === 'without_discount'){
                        sum += parseFloat(((orderLine.get_lst_price() - orderLine.get_unit_price()) * orderLine.get_quantity()));
                    }
                    return sum;
                }
                else{
                    sum += parseFloat(orderLine.get_discount());
                    if (orderLine.display_discount_policy() === 'without_discount'){
                        sum += parseFloat(((orderLine.get_lst_price() - orderLine.get_unit_price()) * orderLine.get_quantity()));
                    }
                    return sum;
                }
            }
            else{
                if (self.pos.config.discount_type == 'percentage'){
                    sum += parseFloat(orderLine.get_unit_price() * (orderLine.get_discount()/100) * orderLine.get_quantity());
                    if (orderLine.display_discount_policy() === 'without_discount'){
                        sum += parseFloat(((orderLine.get_lst_price() - orderLine.get_unit_price()) * orderLine.get_quantity()));
                    }
                    return sum;
                }
                if(self.pos.config.discount_type == 'fixed'){
                    sum += parseFloat(orderLine.get_discount());
                    if (orderLine.display_discount_policy() === 'without_discount'){
                        sum += parseFloat(((orderLine.get_lst_price() - orderLine.get_unit_price()) * orderLine.get_quantity()));
                    }
                    return sum;
                }
            }
        }), 0), this.pos.currency.rounding);
    },

    init_from_JSON(json){
        super.init_from_JSON(...arguments);
        this.total_qty = json.total_qty || 0;
        this.set_total_qty(json.total_qty);
        this.barcode = json.barcode || "";
        this.return_order_ref = json.return_order_ref || false;
        this.imported_sales = json.imported_sales || [];
        this.is_coupon_used = json.is_coupon_used || false;
        this.coupon_id = json.coupon_id;
        this.coup_maxamount = json.coup_maxamount;
    },

    export_as_JSON(){
        const json = super.export_as_JSON(...arguments);
        json.total_qty = this.get_total_qty_value() || 0;
        json.return_order_ref = this.return_order_ref || false;
        json.barcode = this.barcode;
        json.imported_sales = this.imported_sales || [];
        // json.discount_type = this.discount_type || false;
        json.discount_type = this.pos.config.discount_type || false;
        json.is_coupon_used = this.is_coupon_used || false;
        json.coupon_id = this.coupon_id;
        json.coup_maxamount = this.coup_maxamount;
        return json;
    },

    export_for_printing() {
        const json = super.export_for_printing(...arguments);
        json.total_qty = this.get_total_qty_value()|| 0;
        json.barcode = this.barcode;
        return json;
    },

    get_total_qty_value(){
        let lines =  this.get_orderlines();
        var total_qty = 0;
        lines.map((line) => total_qty += line.quantity)
        return total_qty
        
    },

    async pay() {
        var self = this;
        let order = this.pos.get_order();
        let lines = order.get_orderlines();
        let pos_config = self.pos.config; 
        let allow_order = pos_config.pos_allow_order;
        let deny_order= pos_config.pos_deny_order || 0;
        let call_super = true;

        if(pos_config.display_stock){
            let prod_used_qty = {};
            $.each(lines, function( i, line ){
                let prd = line.product;
                if (prd.type == 'product'){
                    if(pos_config.pos_stock_type == 'onhand'){
                        if(prd.id in prod_used_qty){
                            let old_qty = prod_used_qty[prd.id][1];
                            prod_used_qty[prd.id] = [prd.bi_on_hand,line.quantity+old_qty]
                        }else{
                            prod_used_qty[prd.id] = [prd.bi_on_hand,line.quantity]
                        }
                    }
                    if(pos_config.pos_stock_type == 'available'){
                        if(prd.id in prod_used_qty){
                            let old_qty = prod_used_qty[prd.id][1];
                            prod_used_qty[prd.id] = [prd.bi_available,line.quantity+old_qty]
                        }else{
                            prod_used_qty[prd.id] = [prd.bi_available,line.quantity]
                        }
                    }                    
                }
            });

            $.each(prod_used_qty,await function( i, pq ){
                let product = self.pos.db.get_product_by_id(i);
                if (allow_order == false && pq[0] < pq[1]){
                    call_super = false;
                    self.pos.popup.add(ErrorPopup, {
                        title: _t('Deny Order'),
                        body: _t("Deny Order" + "(" + product.display_name + ")" + " is Out of Stock."),
                    });
                }
                let check = pq[0] - pq[1];
                if (allow_order == true && check < deny_order){
                    call_super = false;
                    self.pos.popup.add(ErrorPopup, {
                        title: _t('Deny Order'),
                        body: _t("Deny Order" + "(" + product.display_name + ")" + " is Out of Stock."),
                    });
                }
            });
        }

        if(call_super){
            super.pay();
        }
    },

});

patch(Orderline.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.original_line_id = this.original_line_id || false;
        this.discount_type = this.pos.config.discount_type;
        this.is_coupon_line = this.is_coupon_line || false;
    },

    set_is_coupon_line(is_coupon_line){
        this.is_coupon_line = is_coupon_line;
    },

    get_is_coupon_line(is_coupon_line){
        return this.is_coupon_line;
    },

    set_original_line_id(original_line_id){
        this.original_line_id = original_line_id;
    },

    get_original_line_id(){
        return this.original_line_id;
    },

    init_from_JSON(json){
        super.init_from_JSON(...arguments);
        this.original_line_id = json.original_line_id;
        this.is_coupon_line = json.is_coupon_line || false;
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.original_line_id = this.original_line_id || false;
        json.discount_type = this.pos.config.discount_type || false;
        json.is_coupon_line = this.is_coupon_line || false;
        return json;
    },

    set_discount(discount){

        var parsed_discount =
            typeof discount === "number"
                ? discount
                : isNaN(parseFloat(discount))
                ? 0
                : oParseFloat("" + discount);

        if (parsed_discount < 0) {
            this.discount = 0;
        } else {
            if (this.refunded_orderline_id){
                if(this.discount){
                    if (this.discount_type == 'percentage'){
                        var disc = Math.min(Math.max(parseFloat(parsed_discount) || 0, 0),100);
                    }


                    if (this.discount_type == 'fixed'){
                        var disc = parsed_discount || 0;
                    }
                }

            }
            else{

                if (this.pos.config.discount_type == 'percentage'){
                    var disc = Math.min(Math.max(parseFloat(parsed_discount) || 0, 0),100);
                }
                if (this.pos.config.discount_type == 'fixed'){
                    if (this.pos.mainScreen.component){
                        if (this.pos.mainScreen.component.name == 'ProductScreen'){
                            let prod_price = this.get_unit_price() * this.get_quantity()
                            if (prod_price > parsed_discount){
                                var disc = parsed_discount;
                            }else{
                                if (prod_price == 0){
                                    var disc = Math.min(Math.max(parseFloat(parsed_discount) || 0, 0),100);
                                }else{
                                    var disc = prod_price;
                                }
                            }
                        }else{
                            var disc = parsed_discount;
                        }
                    }
                   
                }
            }
            this.discount = disc;
            this.discountStr = '' + disc;
        }
    },

    get_base_price(){
        var rounding = this.pos.currency.rounding;
        if(this.discount_type){
            if (this.discount_type == 'percentage')
            {
                return round_pr(this.get_unit_price() * this.get_quantity() * (1 - this.get_discount()/100), rounding);
            }
            if (this.discount_type == 'fixed')
            {
                let base_price = round_pr((this.get_unit_price()* this.get_quantity())-(this.get_discount()), rounding)
                if (this.refunded_orderline_id){
                    if (this.get_unit_price() == 0){
                        return 0;
                    }else{

                        return round_pr((this.get_unit_price()* this.get_quantity())+(this.get_discount()), rounding);  
                    }
                }else{

                    if (base_price < 0){
                        return 0.0;
                    }else{
                        return round_pr((this.get_unit_price()* this.get_quantity())-(this.get_discount()), rounding); 
                    }
                }
                 
            }
        }else{
            if (this.pos.config.discount_type == 'percentage')
            {
                return round_pr(this.get_unit_price() * this.get_quantity() * (1 - this.get_discount()/100), rounding);
            }
            if (this.pos.config.discount_type == 'fixed')
            {
                return round_pr((this.get_unit_price()* this.get_quantity())-(this.get_discount()), rounding);  
            }
        }
    },


    get_all_prices(qty = this.get_quantity()) {
        var price_unit;
        if(this.pos.config.discount_type){
            if (this.pos.config.discount_type == 'percentage'){
                price_unit = this.get_unit_price() * (1.0 - (this.get_discount() / 100.0));
            }
            if (this.pos.config.discount_type == 'fixed'){
               if (this.get_discount() == 0){
                    price_unit = this.get_unit_price();
                }else{
                    price_unit = this.get_base_price()/this.get_quantity();   
                    //price_unit = this.get_unit_price() - this.get_discount(); 
                }
            }

        }else{
            price_unit = this.get_unit_price() * (1.0 - this.get_discount() / 100.0);
        }
        var taxtotal = 0;

        var product = this.get_product();
        var taxes_ids = this.tax_ids || product.taxes_id;
        taxes_ids = taxes_ids.filter((t) => t in this.pos.taxes_by_id);
        var taxdetail = {};
        var product_taxes = this.pos.get_taxes_after_fp(taxes_ids, this.order.fiscal_position);

        var all_taxes = this.compute_all(
            product_taxes,
            price_unit,
            qty,
            this.pos.currency.rounding
        );
        var all_taxes_before_discount = this.compute_all(
            product_taxes,
            this.get_unit_price(),
            qty,
            this.pos.currency.rounding
        );
        all_taxes.taxes.forEach(function (tax) {
            taxtotal += tax.amount;
            taxdetail[tax.id] = {
                amount: tax.amount,
                base: tax.base,
            };
        });

        return {
            priceWithTax: all_taxes.total_included,
            priceWithoutTax: all_taxes.total_excluded,
            priceWithTaxBeforeDiscount: all_taxes_before_discount.total_included,
            priceWithoutTaxBeforeDiscount: all_taxes_before_discount.total_excluded,
            tax: taxtotal,
            taxDetails: taxdetail,
        };
    },

   
    get_orderline_discount_type(){
        return this.pos.config.discount_type;
    },

    getPriceString(){
        if (this.pos.config.discount_type == 'fixed'){
            return this.comboLines && this.comboLines.length > 0
            ? // empty string if it is a combo parent line
            ""
            : this.env.utils.formatCurrency(this.get_display_price(), this.currency);
        }else{
            return this.get_discount_str() === "100"
            ? // free if the discount is 100
            _t("Free")
            : (this.comboLines && this.comboLines.length > 0)
            ? // empty string if it is a combo parent line
            ""
            : this.env.utils.formatCurrency(this.get_display_price(), this.currency);
        }
    },

    getDisplayData() {
        return {
                    productName: this.get_full_product_name(),
                    price:this.getPriceString(),
                    qty: this.get_quantity_str(),
                    unit: this.get_unit().name,
                    unitPrice: this.env.utils.formatCurrency(this.get_unit_display_price()),
                    oldUnitPrice: this.env.utils.formatCurrency(this.get_old_unit_display_price()),
                    discount: this.get_discount_str(),
                    customerNote: this.get_customer_note(),
                    internalNote: this.getNote(),
                    comboParent: this.comboParent?.get_full_product_name(),
                    pack_lot_lines: this.get_lot_lines(),
                    price_without_discount: this.env.utils.formatCurrency(this.getUnitDisplayPriceBeforeDiscount()),
                    discount_type : this.get_orderline_discount_type(),
                    line_discount_type : this.pos.config.discount_type,
                    attributes: this.attribute_value_ids
                        ? this.findAttribute(this.attribute_value_ids, this.custom_attribute_value_ids)
                        : [],
        };
    },

    get_display_price_one(){
        var rounding = this.pos.currency.rounding;
        var price_unit = this.get_unit_price();
        if (this.pos.config.iface_tax_included !== 'total') {

            if(this.discount_type){
                if (this.discount_type == 'Percentage')
                {
                    return round_pr(price_unit * (1.0 - (this.get_discount() / 100.0)), rounding);
                }
                if (this.discount_type == 'Fixed')
                {
                    return round_pr((price_unit*this.get_quantity())  - this.get_discount(), rounding);
                }
            }
            else{

                if (this.pos.config.discount_type == 'percentage')
                {
                    return round_pr(price_unit * (1.0 - (this.get_discount() / 100.0)), rounding);
                }
                if (this.pos.config.discount_type == 'fixed')
                {
                    return round_pr((price_unit*this.get_quantity())  - this.get_discount(), rounding);
                }
            }   

        } else {
            var product =  this.get_product();
            var taxes_ids = product.taxes_id;
            var taxes =  this.pos.taxes;
            var product_taxes = [];

            _(taxes_ids).each(function(el){
                product_taxes.push(_.detect(taxes, function(t){
                    return t.id === el;
                }));
            });

            var all_taxes = this.compute_all(product_taxes, price_unit, 1, this.pos.currency.rounding);
            if (this.discount_type){
                if (this.discount_type == 'Percentage')
                {
                    return round_pr(all_taxes.total_included * (1 - this.get_discount()/100), rounding);
                }
                if (this.discount_type == 'Fixed')
                {
                    return round_pr((all_taxes.total_included * this.get_quantity()) - this.get_discount(), rounding);
                }
            }else{
                if (this.pos.config.discount_type == 'percentage')
                {
                    return round_pr(all_taxes.total_included * (1 - this.get_discount()/100), rounding);
                }
                if (this.pos.config.discount_type == 'fixed')
                {
                    return round_pr((all_taxes.total_included * this.get_quantity()) - this.get_discount(), rounding);
                }
            }   
        }
    }
});