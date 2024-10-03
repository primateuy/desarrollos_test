/** @odoo-module **/

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup"; 
import { _t } from "@web/core/l10n/translation";

export class CreateDraftPOS extends Component {
    static template = "pos_all_in_one.CreateDraftPOS";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }

    async onClickDraft() {
        let self = this;
        let order = this.pos.get_order();
        let orderlines = order.get_orderlines();
        let partner_id = order.get_partner();
        if (!partner_id){
            return self.popup.add(ErrorPopup, {
                title: _t('Unknown customer'),
                body: _t('You cannot Create Order.Select customer first.'),
            });
        }
        else if(orderlines.length === 0){
            return  self.popup.add(ErrorPopup, {
                title: _t('Empty Order'),
                body: _t('There must be at least one product in your order.'),
            });
        }
        else if(order.to_invoice){
            return  self.popup.add(ErrorPopup, {
                'title': _t('Order Validation'),
                'body': _t('You Can not create invoice for draft order,please uncheck "Invoice" from payment screen.'),
            });
            return;
        }
        else{
            if(order.get_total_with_tax() !== order.get_total_paid()){
                order.amount_due = order.get_due();
                order.is_draft_order = true;
                order.is_partial = true;
                order.to_invoice = false;
                self.pos.push_single_order(order);
                self.pos.showScreen('ReceiptScreen');           
            }
        }
    }
}

ProductScreen.addControlButton({
    component: CreateDraftPOS,
    condition: function () {
        return this.pos.config.allow_partical_payment;
    },
});