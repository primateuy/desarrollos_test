/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { Order, Orderline, Payment } from "@point_of_sale/app/store/models";
import { ProductTemplatePopup } from "@pos_all_in_one/app/popup/product_template_popup";
import { omit } from "@web/core/utils/objects";


patch(PosStore.prototype, {
    // @Override
    async _processData(loadedData) {
        await super._processData(loadedData);
        let self = this;
        self.pos_category = loadedData['pos_category'] || [];
        this.product_categories = loadedData['product.category']
        self.product_templates = loadedData['product.template'] || [];
        self.db.product_template_by_id = {};
        this.db.product_tmpl_id = [];
        self.db.add_product_templates(self.product_templates);

        this.stockwarehouse = loadedData['stock.warehouse'] || [];
        this.stockpickingtype = loadedData['pos_stock_picking'] || [];
        
        this.stocklocations = loadedData['stock.location'] || [];
        this.stockpicking = loadedData['stock.picking'] || [];

        this.poscurrency = loadedData['poscurrency'] || [];

        this.pos_sessions = loadedData['pos_sessions'] || [];
        this.locations = loadedData['stock.location'] || [];

        self.pos_loyalty_setting = loadedData['pos.loyalty.setting'] || [];
        self.pos_redeem_rule = loadedData['pos.redeem.rule'] || [];


        this.account_move = loadedData['account.move'] || [];
        // this._loadAccountmove(loadedData['account.move']);

        this.account_journal = loadedData['account.journal'] || [];
        // this._loadAccountjournal(loadedData['account.journal']);

        this.db.invoice_sorted = [];
        this.db.invoice_by_id = {};
        this.db.invoice_line_id = {};
        this.db.invoice_search_string = "";
        this.db.invoice_write_date = null;

        this.pos_order = loadedData['pos_order'] || [];
    },

    _loadAccountmove(invoices){
        var self = this;
        self.invoices = invoices;

        self.get_invoices_by_id = [];
        invoices.forEach(function(invoice) {
            self.get_invoices_by_id[invoice.id] = invoice;
        });
    },

    _loadAccountjournal(journals){
        var self = this;
        self.journals = journals;
    },

    _loadProductCategory(product_categories){
        var category_by_id = {};

        product_categories.forEach(function (category) {
           category_by_id[category.id] = category;
        });

        product_categories.forEach(function (category) {
           category.parent = category_by_id[category.parent_id[0]];
        });
        this.product_categories = product_categories;
    },

    load_new_invoices(){
        var self = this;
        var def  = new $.Deferred();
        var fields = _.find(this.models,function(model){ return model.model === 'account.move'; }).fields;
        var domain = [['move_type','=','out_invoice'], ['state','=','posted'], ['payment_state', '!=', 'paid']];

        rpc.query({
            model: 'account.move',
            method: 'search_read',
            args: [domain, fields],
        }, {
            timeout: 3000,
            shadow: true,
        })
        .then(function(products){
                if (self.db.invoices) {   
                    def.resolve();
                } else {
                    def.reject();
                }
            }, function(err,event){ event.preventDefault(); def.reject(); });
        return def;
    },

    async addProductToCurrentOrder(product, options = {}) {
        var self = this;
        const products = event.detail;
        var product_variant = "";
        if(self.env.services.pos.config.allow_product_variants){
            var prod_template = this.db.product_template_by_id[product.product_tmpl_id];
            var product_template = prod_template ? prod_template : product;
            var prod_list = [];
            if (product_template.product_variant_count > 1){
                product_template.product_variant_ids.forEach((prod) => {
                    prod_list.push(self.env.services.pos.db.get_product_by_id(prod));
                });
                product_variant = prod_list;
                await this.env.services.pos.popup.add(ProductTemplatePopup, {'variant_ids':product_variant});
            }else{
                options = { ...options, ...(await product.getAddProductOptions()) };
                this.env.services.pos.get_order().add_product(product,options)
            }                             
        }else{
            super.addProductToCurrentOrder(product, options = {});
        }    
    },

    async selectPartner() {
        // FIXME, find order to refund when we are in the ticketscreen.
        const currentOrder = this.get_order();
        if(currentOrder.getHasRedeemLine()){
            this.popup.add(ErrorPopup, {
                'title': _t('Cannot Change Customer'),
                'body': _t('Sorry, you redeemed product, please remove it before changing customer.'),
            }); 
        }else{
            if (!currentOrder) {
                return;
            }
            const currentPartner = currentOrder.get_partner();
            if (currentPartner && currentOrder.getHasRefundLines()) {
                this.popup.add(ErrorPopup, {
                    title: _t("Can't change customer"),
                    body: _t(
                        "This order already has refund lines for %s. We can't change the customer associated to it. Create a new order for the new customer.",
                        currentPartner.name
                    ),
                });
                return;
            }
            const { confirmed, payload: newPartner } = await this.showTempScreen("PartnerListScreen", {
                partner: currentPartner,
            });
            if (confirmed) {
                currentOrder.set_partner(newPartner);
            }
        }
    }
    
});

patch(Payment.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.pos_reference = this.pos_reference || "";

        this.currency_amount = this.currency_amount || 0.0;
        this.currency_name = this.currency_name || this.pos.currency.name;
        this.currency_symbol = this.currency_symbol || this.pos.currency.symbol;
    },

    set_curname(currency_name){
        this.currency_name = currency_name;
    },

    set_curamount(currency_amount){
        this.currency_amount = currency_amount;
    },

    set_currency_symbol(currency_symbol){
        this.currency_symbol = currency_symbol;
    },
    
    set_pos_reference(pos_reference){
        this.pos_reference = pos_reference;
    },

    get_pos_reference(){
        return this.pos_reference;
    },
    
    init_from_JSON(json){
        super.init_from_JSON(...arguments);
        this.pos_reference = json.pos_reference || "";
        this.currency_amount = json.currency_amount || 0.0;
        this.currency_name = json.currency_name || this.pos.currency.name;
        this.currency_symbol = json.currency_symbol || this.pos.currency.symbol;
    },

    export_as_JSON(){
        const json = super.export_as_JSON(...arguments);
        json.pos_reference = this.pos_reference || "";
        json.currency_amount = this.currency_amount || 0.0;
        json.currency_name = this.currency_name || this.pos.currency.name;
        json.currency_symbol = this.currency_symbol || this.pos.currency.symbol;
        return json;
    },

    export_for_printing() {
        const json = super.export_for_printing(...arguments);
        json.pos_reference = this.pos_reference || "";
        json.currency_amount = this.currency_amount || 0.0;
        json.currency_name = this.currency_name || this.pos.currency.name;
        json.currency_symbol = this.currency_symbol || this.pos.currency.symbol;
        json.cust_order = this;
        return json;
    },
});

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
        this.currency_amount = this.currency_amount || "";
        this.currency_symbol = this.currency_symbol || "";
        this.currency_name = this.currency_name || "";
        this.loyalty = this.loyalty  || 0;
        this.redeemed_points = this.redeemed_points || 0;
        this.redeem_done = this.redeem_done || false;
        this.remove_true = this.remove_true || false;
        this.redeem_point = this.redeem_point || 0;
        this.remove_line = this.remove_line || false;
        this.is_partial    = false;
        this.is_paying_partial    = false;
        this.amount_due    = 0;
        this.amount_paid    = 0;
        this.is_draft_order = false;
        this.set_is_partial();
    },

    set_is_partial(set_partial){
        this.is_partial = set_partial || false;
    },

    getHasRedeemLine() {
        for (const line of this.get_orderlines()) {
            if (line.cust_redeem_line) {
                return true;
            }
        }
        return false;
    },

    set_symbol(currency_symbol){
        this.currency_symbol = currency_symbol;
    },

    set_curamount(currency_amount){
        this.currency_amount = currency_amount;
    },

    set_curname(currency_name){
        this.currency_name = currency_name;
    },

    get_curamount(currency_amount){
        return this.currency_amount;
    },

    get_symbol(currency_symbol){
        return this.currency_symbol;
    },

    get_curname(currency_name){
        return this.currency_name;
    },

    get_partial_due(){
        let due = 0;
        if(this.get_due() > 0){
            due = this.get_due();
        }
        return due
    },

    init_from_JSON(json){
        super.init_from_JSON(...arguments);
        this.currency_amount = json.currency_amount || "";
        this.currency_symbol = json.currency_symbol || "";
        this.currency_name = json.currency_name || "";
        this.loyalty = json.loyalty;
        this.redeem_done = json.redeem_done;
        this.redeemed_points = json.redeemed_points;
        this.remove_true = json.remove_true || false;
        this.redeem_point = json.redeem_point || 0;
        this.remove_line = json.remove_line || false;
        this.is_partial = json.is_partial;
        this.amount_due = json.amount_due;
        this.is_paying_partial = json.is_paying_partial;
        this.is_draft_order = json.is_draft_order;
    },

    export_as_JSON(){
        const json = super.export_as_JSON(...arguments);
        json.currency_amount = this.get_curamount() || 0.0;
        json.currency_symbol = this.get_symbol() || false;
        json.currency_name = this.get_curname() || false;
        json.redeemed_points = this.redeemed_points;
        json.loyalty = this.get_loyalty_points();
        json.redeem_done = this.redeem_done;
        json.remove_true = this.remove_true || false;
        json.redeem_point = this.redeem_point || 0;
        json.remove_line = this.remove_line || false;
        json.is_partial = this.is_partial || false;
        json.amount_due = this.get_partial_due();
        json.is_paying_partial = this.is_paying_partial;
        json.is_draft_order = this.is_draft_order || false;
        return json;
    },

    export_for_printing() {
        const json = super.export_for_printing(...arguments);
        json.currency_amount = this.get_curamount() || 0.0;
        json.currency_symbol = this.get_symbol() || false;
        json.currency_name = this.get_curname() || false;
        json.cust_order = this;

        let orderlines_list = []
        
        this.orderlines.forEach((line) => {
            if((this.is_paying_partial == false) || (this.is_paying_partial == true && line.price > 0)){
                orderlines_list.push(line);
            }
        });

        json['orderlines'] = orderlines_list.map((l) => omit(l.getDisplayData(), "internalNote"));
        return json;
    },

    get_redeemed_points(){
        return this.redeemed_points;
    },

    set_loyalty_value(loaylty_point){
        this.loyalty = parseFloat(loaylty_point.toFixed(2));
    },

    get_loyalty_points () {
        return this.loyalty;
    },

    get_total_loyalty(){
        
        let rounding = this.pos.currency.rounding;
        let final_loyalty = 0
        let order = this.pos.get_order();
        let orderlines = this.get_orderlines();
        let partner_id = this.get_partner();
        if(order){
            if(this.pos.pos_loyalty_setting.length != 0){   
                if (this.pos.pos_loyalty_setting[0].loyalty_basis_on == 'pos_category') {
                    if (partner_id){
                        let loyalty = 0;
                        for (let i = 0; i < orderlines.length; i++) {
                            let lines = orderlines[i];
                            let cat_ids = this.pos.db.get_category_by_id(lines.product.bi_pos_reports_catrgory[0])
                            if(cat_ids){
                                if (cat_ids['Minimum_amount']>0){
                                    final_loyalty += lines.get_price_with_tax() / cat_ids['Minimum_amount'];
                                }
                            }
                        }
                        this.set_loyalty_value(parseFloat(final_loyalty.toFixed(2)))
                        return parseFloat(final_loyalty.toFixed(2));
                    }
                }else if (this.pos.pos_loyalty_setting[0].loyalty_basis_on == 'amount') {
                    let loyalty_total = 0;
                    if(order.get_partner()){
                        if (order && partner_id){
                            let amount_total = order.get_total_with_tax();
                            let subtotal = order.get_total_without_tax();
                            let loyaly_points = this.pos.pos_loyalty_setting[0].loyality_amount;
                            final_loyalty += (amount_total / loyaly_points);
                            loyalty_total = order.get_partner().loyalty_points1 + final_loyalty;
                            this.set_loyalty_value(final_loyalty)
                            return parseFloat(final_loyalty.toFixed(2));
                        }
                    }
                }
            }
            return parseFloat(final_loyalty.toFixed(2));
        }
    },
});

patch(Orderline.prototype, {
    setup() {
        super.setup(...arguments);
        this.cust_redeem_line = this.cust_redeem_line  || false;
    },

    get_cust_redeem_line(){
        return this.cust_redeem_line;
    },

    set_cust_redeem_line(cust_redeem_line){
        this.cust_redeem_line = cust_redeem_line;
    },

    init_from_JSON(json){
        super.init_from_JSON(...arguments);         
        this.cust_redeem_line = json.cust_redeem_line || false;
    },

    export_as_JSON(){
        const json = super.export_as_JSON(...arguments);            
        json.cust_redeem_line = this.cust_redeem_line || false;
        return json;
    },

});