/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosOrdersScreen } from "@pos_orders_all/app/screens/product_screen/pos_orders_screen/pos_orders_screen";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup"; 
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { _t } from "@web/core/l10n/translation";


patch(PosOrdersScreen.prototype, {
    setup() {
		super.setup()
		this.filter_state = '';
		this.state = {
			filter_state: this.filter_state,
			filter_option:[],
		};
	},
	
	draftFilter(){
		this.state.filter_state  = 'Unpaid/Draft';
		this.state.query = 'draft';
		const pos_orders = this.pos_orders;
		this.render();
	},
	paidFilter(){
		this.state.filter_state  = 'Paid';
		this.state.query = 'paid';
		const pos_orders = this.pos_orders;
		this.render();
	},
	doneFilter(){
		this.state.filter_state  = 'Posted';
		this.state.query = 'done';
		const pos_orders = this.pos_orders;
		this.render();
	},
	invoicedFilter(){
		this.state.filter_state  = 'Invoiced';
		this.state.query = 'invoiced';
		const pos_orders = this.pos_orders;
		this.render();
	},
	refresh_orders(){
		$('.input-search-orders').val('');
		this.state.query = '';
		this.props.selected_partner_id = false;
		this.state.filter_state  = '';
		this.render();
	},

	remove_current_orderlines(){
		let self = this;
		let order = self.pos.get_order();
		let orderlines = order.get_orderlines();
		order.set_partner(null);           
        while (orderlines.length > 0) {
            orderlines.forEach(function (line) {
                order.removeOrderline(line);
            });
        }
	},

	async clickPayCustom(event){
		let self = this;
		let old_order = self.pos.get_order();
		let order = event;

		let o_id = parseInt(event.id);
		let orderlines = [];
		let amount_due = order.amount_total - order.amount_paid
		$.each(order.lines, function(index, value) {
			let ol = self.pos.db.get_orderline_by_id[value];
			orderlines.push(ol);
		});
		self.remove_current_orderlines();
		if(orderlines.length > 0){
			old_order.name = order.pos_reference;
			old_order.is_partial = order.is_partial;
			old_order.amount_due = order.amount_total - order.amount_paid;
			old_order.barcode = order.barcode;
			old_order.barcode_img = order.barcode_img;
			old_order.is_paying_partial = true;
			old_order.amount_paid  = order.amount_paid;
		}

		if (order.partner_id) {
			let partner = self.pos.db.get_partner_by_id(order.partner_id[0]);
			old_order.set_partner(partner);
		}

		orderlines.forEach(function(ol) {
			let product = self.pos.db.get_product_by_id(ol.product_id[0]);
			old_order.add_product(product, {
				quantity: parseFloat(ol.qty),
				price: ol.price_unit,
				discount: ol.discount,
			});
		});

		if(amount_due > 0 && order.amount_paid != 0)
		{
			let product_for_due = self.pos.config.partial_product_id;
			if(product_for_due)
			{
				let prd = self.pos.db.get_product_by_id(product_for_due[0]);
				if(prd == undefined){
					self.popup.add(ErrorPopup, {
						title: _t('Configure Product'),
						body: _t('Maybe the product is not loaded properly or restricted the product category.'),
					});
				}else{
					old_order.add_product(prd,{
						quantity: 1.0,
						price: -order.amount_paid,
						discount: 0
					});							
				}
			}
			else{
				return self.popup.add(ErrorPopup, {
					title: _t('Configure Product'),
					body: _t('Please configure partial product.'),
				});
			}
		}
		if(old_order.orderlines.length > 0){
			self.pos.showScreen('PaymentScreen');			
		}
	},
});