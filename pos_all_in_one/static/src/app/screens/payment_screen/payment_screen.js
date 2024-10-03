/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { Component, onMounted, useRef } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { ConnectionLostError } from "@web/core/network/rpc_service";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { useService } from "@web/core/utils/hooks";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(PaymentScreen.prototype, {
    setup() {
		super.setup();
		this.mobile_multi = false

		onMounted(() => {
           	$('#details_mobile').hide()
        });

		this.pos = usePos();
        this.popup = useService("popup");
        this.orm = useService("orm");
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
            orderlines = order.get_orderlines();
        }
        order.is_paying_partial=false
	},

	async click_back(){
		let self = this;
		if(this.currentOrder.is_paying_partial){
			const { confirmed } = await self.popup.add(ConfirmPopup, {
				title: _t('Cancel Payment ?'),
				body: _t('Are you sure,You want to Cancel this payment?'),
			});
			if (confirmed) {
				debugger;
				self.remove_current_orderlines();
				self.pos.showScreen('ProductScreen');
			}
		}
		else{
			self.pos.showScreen('ProductScreen');
		}
	},

	clickPayLater(){
		let self = this;
		let order = self.pos.get_order();
		let orderlines = order.get_orderlines();
		let partner_id = order.get_partner();
		if (!partner_id){
			return self.popup.add(ErrorPopup, {
				title: _t('Unknown customer'),
				body: _t('You cannot perform partial payment.Select customer first.'),
			});
		}
		else if(orderlines.length === 0){
			return self.popup.add(ErrorPopup, {
				title: _t('Empty Order'),
				body: _t('There must be at least one product in your order.'),
			});
		}
		else{
			order.is_partial = true;
			order.amount_due = order.get_due();
			order.set_is_partial(true);
			order.to_invoice = false;
			order.finalized = true;
			self.pos.push_single_order(order);
			self.pos.showScreen('ReceiptScreen');						
		}
	},

	_UpdateDetails() {
		if($("#cur-switch").prop('checked') == true){
			$('#details').hide()
		}
		else{
			$('#details').show()
		}
	},

	_UpdateDetailsMobile() {
		$(".js_multi").toggleClass("highlight");
		if(this.mobile_multi == true){
			$('#details_mobile').hide()
			
			this.mobile_multi = false
		}else{
			$('#details_mobile').show()
			this.mobile_multi = true
		}
	},

	get check_mobile_multi(){
		return this.mobile_multi;
	},

	_UpdateAmountt() {
		let self = this;
		let order = this.pos.get_order();
		let paymentlines = this.pos.get_order().get_paymentlines();
		let open_paymentline = false;
		let tot = order.get_curamount();
		let tot_amount = 0;
		let currency = this.pos.poscurrency;
		let user_amt = $('.edit-amount').val();
		let cur = $('.drop-currency').val();
		let payment_methods_from_config = this.pos.payment_methods.filter(method => this.pos.config.payment_method_ids.includes(method.id));
		order.add_paymentline(payment_methods_from_config[0]);
		let selected_paymentline = order.selected_paymentline;
		if (user_amt == ''){
		}else{

			for(var i=0;i<currency.length;i++){
				if(cur==currency[i].id){
					let c_rate = self.pos.currency.rate/currency[i].rate;
					tot_amount = parseFloat(user_amt)*c_rate;
					selected_paymentline.amount =parseFloat(tot_amount.toFixed(2));

					selected_paymentline.amount_currency =parseFloat(parseFloat(user_amt).toFixed(2)) ;
					$('.show-payment').text((selected_paymentline.amount));
					selected_paymentline.set_curname(currency[i].name);
					selected_paymentline.set_curamount(selected_paymentline.amount_currency);
					selected_paymentline.set_currency_symbol(currency[i].symbol);
				}
			}
			order.get_paymentlines();
			if (!order) {
				return;
			} else if (order.is_paid()) {
				$('.next').addClass('highlight');
			}else{
				$('.next').removeClass('highlight');
			}
			$('.edit-amount').val('');
			self._ChangeCurrency();
			window.document.body.removeEventListener('keypress', self.keyboard_handler);
			window.document.body.removeEventListener('keydown', self.keyboard_keydown_handler);
		}
		
	},

	_ChangeCurrency() {
		let self = this;
		let currencies = this.pos.poscurrency;
		let cur = $('.drop-currency').val();
		let curr_sym;
		let order= this.pos.get_order();
		let pos_currency = this.pos.currency;
		for(var i=0;i<currencies.length;i++){
			if(cur != pos_currency.id && cur==currencies[i].id){
				let currency_in_pos = (currencies[i].rate/self.pos.currency.rate).toFixed(6);
				$('.currency_symbol').text(currencies[i].symbol);
				$('.currency_rate').text(currency_in_pos);
				curr_sym = currencies[i].symbol;

				let curr_tot =order.get_due()*currency_in_pos;
				$('.currency_cal').text(parseFloat(curr_tot.toFixed(6)));
				order.set_curamount(parseFloat(curr_tot.toFixed(6)));
				order.set_symbol(curr_sym);
				order.set_curname(currencies[i].name);
				return curr_tot;
			}
			if(cur == pos_currency.id && cur==currencies[i].id){
				$('.currency_symbol').text(pos_currency.symbol);
				$('.currency_rate').text(1);
				curr_sym = pos_currency.symbol;

				let curr_tot =order.get_due();
				$('.currency_cal').text(parseFloat(curr_tot.toFixed(2)));
				order.set_curamount(parseFloat(curr_tot.toFixed(2)));
				order.set_symbol(curr_sym);
				order.set_curname(pos_currency.name);
				return curr_tot;
			}
		}
	},

	async _finalizeValidation() {
        if (this.currentOrder.is_paid_with_cash() || this.currentOrder.get_change()) {
            this.hardwareProxy.openCashbox();
        }

        this.currentOrder.date_order = luxon.DateTime.now();
        for (const line of this.paymentLines) {
            if (!line.amount === 0) {
                this.currentOrder.remove_paymentline(line);
            }
        }
        this.currentOrder.finalized = true;

        // 1. Save order to server.
        this.env.services.ui.block();
        const syncOrderResult = await this.pos.push_single_order(this.currentOrder);
        this.env.services.ui.unblock();

        if (syncOrderResult instanceof ConnectionLostError) {
        	
        	if (self.currentOrder.get_partner()){
				let get_loyalty = self.currentOrder.get_partner().id
				const loyalty_point = await this.orm.call("res.partner", "updated_rec", [get_loyalty]);

				if (loyalty_point){
					self.currentOrder.get_partner().loyalty_points1 = loyalty_point;
				}
			}

            this.pos.showScreen(this.nextScreen);
            return;
        } else if (!syncOrderResult) {
            return;
        }

        try {
            // 2. Invoice.
            if (this.shouldDownloadInvoice() && this.currentOrder.is_to_invoice()) {
                if (syncOrderResult[0]?.account_move) {
                    await this.report.doAction("account.account_invoices", [
                        syncOrderResult[0].account_move,
                    ]);
                } else {
                    throw {
                        code: 401,
                        message: "Backend Invoice",
                        data: { order: this.currentOrder },
                    };
                }
            }
        } catch (error) {
            if (error instanceof ConnectionLostError) {
                Promise.reject(error);
                return error;
            } else {
                throw error;
            }
        }

        // 3. Post process.
        if (
            syncOrderResult &&
            syncOrderResult.length > 0 &&
            this.currentOrder.wait_for_push_order()
        ) {
            await this.postPushOrderResolve(syncOrderResult.map((res) => res.id));
        }

        await this.afterOrderValidation(!!syncOrderResult && syncOrderResult.length > 0);
    },

    async afterOrderValidation(suggestToSync = true) {
        // Remove the order from the local storage so that when we refresh the page, the order
        // won't be there
        var self = this
        this.pos.db.remove_unpaid_order(this.currentOrder);

        // Ask the user to sync the remaining unsynced orders.
        if (suggestToSync && this.pos.db.get_orders().length) {
            const { confirmed } = await this.popup.add(ConfirmPopup, {
                title: _t("Remaining unsynced orders"),
                body: _t("There are unsynced orders. Do you want to sync these orders?"),
            });
            if (confirmed) {
                // NOTE: Not yet sure if this should be awaited or not.
                // If awaited, some operations like changing screen
                // might not work.
                this.pos.push_orders();
            }
        }
        // Always show the next screen regardless of error since pos has to
        // continue working even offline.

        if (self.currentOrder.get_partner()){
			let get_loyalty = self.currentOrder.get_partner().id

			const loyalty_point = await this.orm.call("res.partner", "updated_rec", [get_loyalty]);

			if (loyalty_point){
				self.currentOrder.get_partner().loyalty_points1 = loyalty_point;
			}
		}
        let nextScreen = this.nextScreen;

        if (
            nextScreen === "ReceiptScreen" &&
            !this.currentOrder._printed &&
            this.pos.config.iface_print_auto
        ) {
            const invoiced_finalized = this.currentOrder.is_to_invoice()
                ? this.currentOrder.finalized
                : true;

            if (this.hardwareProxy.printer && invoiced_finalized) {
                const printResult = await this.printer.print(OrderReceipt, {
                    data: this.pos.get_order().export_for_printing(),
                    formatCurrency: this.env.utils.formatCurrency,
                });

                if (printResult && this.pos.config.iface_print_skip_screen) {
                    this.pos.removeOrder(this.currentOrder);
                    this.pos.add_new_order();
                    nextScreen = "ProductScreen";
                }
            }
        }

        this.pos.showScreen(nextScreen);
    }
});
