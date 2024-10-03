/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Order, Payment } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    // @Override
    async _processData(loadedData) {
        await super._processData(...arguments);
        this.poscurrency = loadedData['poscurrency'];
    },
});

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
        this.currency_amount = this.currency_amount || "";
		this.currency_symbol = this.currency_symbol || "";
		this.currency_name = this.currency_name || "";
        
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

	init_from_JSON(json){
		super.init_from_JSON(...arguments);
		this.currency_amount = json.currency_amount || "";
		this.currency_symbol = json.currency_symbol || "";
		this.currency_name = json.currency_name || "";
	},

	export_as_JSON(){
		const json = super.export_as_JSON(...arguments);
		json.currency_amount = this.get_curamount() || 0.0;
		json.currency_symbol = this.get_symbol() || false;
		json.currency_name = this.get_curname() || false;
		return json;
	},

	export_for_printing() {
		const json = super.export_for_printing(...arguments);
		json.currency_amount = this.get_curamount() || 0.0;
		json.currency_symbol = this.get_symbol() || false;
		json.currency_name = this.get_curname() || false;
		return json;
	},
});


patch(Payment.prototype, {
    setup() {
        super.setup(...arguments);
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
	
	init_from_JSON(json){
		super.init_from_JSON(...arguments);
		this.currency_amount = json.currency_amount || 0.0;
		this.currency_name = json.currency_name || this.pos.currency.name;
		this.currency_symbol = json.currency_symbol || this.pos.currency.symbol;
	},

	export_as_JSON(){
		const json = super.export_as_JSON(...arguments);
		json.currency_amount = this.currency_amount || 0.0;
		json.currency_name = this.currency_name || this.pos.currency.name;
		json.currency_symbol = this.currency_symbol || this.pos.currency.symbol;

		return json;
	},

	export_for_printing() {
		const json = super.export_for_printing(...arguments);
		json.currency_amount = this.currency_amount || 0.0;
		json.currency_name = this.currency_name || this.pos.currency.name;
		json.currency_symbol = this.currency_symbol || this.pos.currency.symbol;
		return json;
	},
});
