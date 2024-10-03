/** @odoo-module */

import { ProductsWidget } from "@point_of_sale/app/screens/product_screen/product_list/product_list";
import { Product } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { onMounted } from "@odoo/owl";


patch(ProductsWidget.prototype, {
    /**
     * @override
     */

	setup() {
        super.setup();
        this.pos = usePos();
        onMounted(this.onMounted);
    },

    onMounted() {
    	let self = this;
    	self.change_css();
		let config = self.pos.config;
		let color_background = config.color_background;
		let font_color = config.font_background;
		if(config.pos_stock_type == 'onhand' || config.pos_stock_type == 'available'){
			if (config.stock_position == 'top_left'){
				if(color_background){
					$('.qty-left-label').css('background-color', color_background);
					$('.qty-left-label').css('color', font_color);
					$('.qty-image-label').css('background-color', color_background);
					$('.qty-image-label').css('color', font_color);
				}
				else{
					$('.qty-left-label').css('background-color', "#4caf50");
					$('.qty-left-label').css('color', "#ffffff");
					$('.qty-image-label').css('background-color', "#4caf50");
					$('.qty-image-label').css('color', "#ffffff");
				}
			}
			if (config.stock_position == 'top_right'){
				if(color_background){
					$('.qty-tright-label').css('background-color', color_background);
					$('.qty-tright-label').css('color', font_color);
				}
				else{
					$('.qty-tright-label').css('background-color', "#4caf50");
					$('.qty-tright-label').css('color', "#ffffff");
				}
			}
			if (config.stock_position == 'bottom_right'){
				if(color_background){
					$('.qty-bright-label').css('background-color', color_background);
					$('.qty-bright-label').css('color', font_color);
				}
				else{
					$('.qty-bright-label').css('background-color', "4caf50");
					$('.qty-bright-label').css('color', "ffffff");
				}
			}
		}
		self.env.services['bus_service'].addEventListener('notification', ({ detail: notifications }) => {
			self.syncProdData(notifications);
		});
    },

    change_css(){
		var self = this;
		let order=self.pos.get_order();
		if(order){
			var interval = setInterval(function () {
				self.interval = interval;
				order.set_interval(interval)
				let config = self.pos.config;
				let color_background = config.color_background;
				let font_color = config.font_background;
				if(config.pos_stock_type == 'onhand' || config.pos_stock_type == 'available'){
					if (config.stock_position == 'top_left'){
						if(color_background){
							$('.qty-left-label').css('background-color', color_background);
							$('.qty-left-label').css('color', font_color);
							$('.qty-image-label').css('background-color', color_background);
							$('.qty-image-label').css('color', font_color);
						}
						else{
							$('.qty-left-label').css('background-color', "#4caf50");
							$('.qty-left-label').css('color', "#ffffff");
							$('.qty-image-label').css('background-color', "#4caf50");
							$('.qty-image-label').css('color', "#ffffff");
						}
					}
					if (config.stock_position == 'top_right'){
						if(color_background){
							$('.qty-tright-label').css('background-color', color_background);
							$('.qty-tright-label').css('color', font_color);
						}
						else{
							$('.qty-tright-label').css('background-color', "#4caf50");
							$('.qty-tright-label').css('color', "#ffffff");
						}
					}
					if (config.stock_position == 'bottom_right'){
						if(color_background){
							$('.qty-bright-label').css('background-color', color_background);
							$('.qty-bright-label').css('color', font_color);
						}
						else{
							$('.qty-bright-label').css('background-color', "4caf50");
							$('.qty-bright-label').css('color', "ffffff");
						}
					}
				}
			},1200)
		}		
	},

    syncProdData(notifications){
		let self = this;
		notifications.forEach(function (ntf) {
			ntf = JSON.parse(JSON.stringify(ntf))
			if(ntf && ntf.type && ntf.type == "product.product/sync_data"){
				let prod = ntf.payload.product[0];
				let old_category_id = self.pos.db.product_by_id[prod.id];
				let new_category_id = prod.pos_categ_ids;
				let stored_categories = self.pos.db.product_by_category_id;

				prod.pos = self.pos;
				if(self.pos.db.product_by_id[prod.id]){

					if(old_category_id.pos_categ_ids){
						for(let old_categ of old_category_id.pos_categ_ids){
							if(!new_category_id.includes(old_categ)){
								stored_categories[old_categ].pop(prod.id)
							}	
						}
						for (let catg_id of new_category_id) {
							if(!stored_categories[catg_id].includes(prod.id)){
								stored_categories[catg_id].push(prod.id)
							}
						}
					}

					if(stored_categories[new_category_id]){
						stored_categories[new_category_id].push(prod.id);
					}
					let updated_prod = self.updateProd(prod);
				}else{
					let updated_prod = self.updateProd(prod);
				}
			}
		});
		let call = self.productsToDisplay;
	},

	updateProd(product){
		let self = this;
		self.pos._loadProductProduct([product]);
		const productMap = {};
		const productTemplateMap = {};

		product.pos = self.pos; 
		product.applicablePricelistItems = {};
		productMap[product.id] = product;
		productTemplateMap[product.product_tmpl_id] = (productTemplateMap[product.product_tmpl_id[0]] || []).concat(product);
		let new_prod =  new Product(product);
		for (let pricelist of self.pos.pricelists) {
			for (const pricelistItem of pricelist.items) {
				if (pricelistItem.product_id) {
					let product_id = pricelistItem.product_id[0];
					let correspondingProduct = productMap[product_id];
					if (correspondingProduct) {
						self.pos._assignApplicableItems(pricelist, correspondingProduct, pricelistItem);
					}
				}
				else if (pricelistItem.product_tmpl_id) {
					let product_tmpl_id = pricelistItem.product_tmpl_id[0];
					let correspondingProducts = productTemplateMap[product_tmpl_id];
					for (let correspondingProduct of (correspondingProducts || [])) {
						self.pos._assignApplicableItems(pricelist, correspondingProduct, pricelistItem);
					}
				}
				else {
					for (const correspondingProduct of product) {
						self.pos._assignApplicableItems(pricelist, correspondingProduct, pricelistItem);
					}
				}
			}
		}
		self.pos.db.product_by_id[product.id] = new_prod ;
	},

	get productsToDisplay() {
        let self = this;
        let prods = super.productsToDisplay;
		let location = self.pos.custom_stock_locations;
		let config = self.pos.config;
		let color_background = config.color_background;
		let font_color = config.font_background;

		if(config.pos_stock_type == 'onhand' || config.pos_stock_type == 'available'){
			if (config.stock_position == 'top_left'){
				if(color_background){
					$('.qty-left-label').css('background-color', color_background);
					$('.qty-left-label').css('color', font_color);
					$('.qty-image-label').css('background-color', color_background);
					$('.qty-image-label').css('color', font_color);
				}
				else{
					$('.qty-left-label').css('background-color', "#4caf50");
					$('.qty-left-label').css('color', "#ffffff");
					$('.qty-image-label').css('background-color', "#4caf50");
					$('.qty-image-label').css('color', "#ffffff");
				}
			}
			if (config.stock_position == 'top_right'){
				if(color_background){
					$('.qty-tright-label').css('background-color', color_background);
					$('.qty-tright-label').css('color', font_color);
				}
				else{
					$('.qty-tright-label').css('background-color', "#4caf50");
					$('.qty-tright-label').css('color', "#ffffff");
				}
			}
			if (config.stock_position == 'bottom_right'){
				if(color_background){
					$('.qty-bright-label').css('background-color', color_background);
					$('.qty-bright-label').css('color', font_color);
				}
				else{
					$('.qty-bright-label').css('background-color', "4caf50");
					$('.qty-bright-label').css('color', "ffffff");
				}
			}
		}
		if (config.show_stock_location == 'specific'){
			if (config.pos_stock_type == 'onhand'){
				$.each(prods, function( i, prd ){
					prd['bi_on_hand'] = 0;
					let loc_onhand = JSON.parse(prd.quant_text);
					$.each(loc_onhand, function( k, v ){
						if(location[0]['id'] == parseInt(k)){
							prd['bi_on_hand'] = v[0];
						}
					})
				});
				this.pos.synch.is_sync = false
			}
			if (config.pos_stock_type == 'available'){
				$.each(prods, function( i, prd ){
					let loc_available = JSON.parse(prd.quant_text);
					prd['bi_available'] = 0;
					let total = 0;
					let out = 0;
					let inc = 0;
					$.each(loc_available, function( k, v ){
						if(location[0]['id'] == parseInt(k)){
							total += v[0];
							if(v[1]){
								out += v[1];
							}
							if(v[2]){
								inc += v[2];
							}
							let final_data = (total + inc)
							prd['bi_available'] = final_data;
							prd['virtual_available'] = final_data;
						}
					})
				});
			}
		}
		else{
			$.each(prods, function( i, prd ){
				prd['bi_on_hand'] = (prd.qty_available);
				prd['bi_available'] = (prd.virtual_available);
			});
		}
		return prods
    }
});
