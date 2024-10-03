/** @odoo-module **/

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { _t } from "@web/core/l10n/translation";
import { Component } from "@odoo/owl";


export class CreateSalesOrderButton extends Component {
    static template = "pos_orders_all.CreateSalesOrderButton";

    setup() {
        super.setup();
        this.pos = usePos();
    }
    
    async click() {
        let self = this;                
        let order = self.pos.get_order();
        var cashier_id = self.pos.get_cashier().id;
        let orderlines = order.get_orderlines();
        let pos_product_list = [];
        let partner_id = false

        if (order.get_partner() != null)
            partner_id = order.get_partner().id;

        if (!partner_id) {
            return self.pos.popup.add(ErrorPopup, {
                title: _t('Unknown customer'),
                body: _t('You cannot Create sale Order. Select customer first.'),
            });
        }

        if (orderlines.length === 0) {
            return self.pos.popup.add(ErrorPopup, {
                title: _t('Empty Order'),
                body: _t('There must be at least one product in your order before Add a note.'),
            });
        }

        for (let i = 0; i < orderlines.length; i++) {
            let product_items = {
                'id': orderlines[i].product.id,
                'quantity': orderlines[i].quantity,
                'uom_id': orderlines[i].product.uom_id[0],
                'price': orderlines[i].price,
                'discount': orderlines[i].discount,
                'discount_method': self.pos.config.discount_type,
            };            
            pos_product_list.push({'product': product_items });
        }

        await this.env.services.orm.call(
            "pos.order",
            "create_sales_order",
            [partner_id, partner_id, pos_product_list, cashier_id],
            ).then(function(output) {
                while (orderlines.length > 0) {
                    orderlines.forEach(function (line) {
                        order.removeOrderline(line);
                    });
                }
                order.set_partner(false);
                alert('Sales Order Created !!!!');
                self.pos.showScreen('ProductScreen')
            }
        );
    }
}

ProductScreen.addControlButton({
    component: CreateSalesOrderButton,
    condition: function () {
        return true;
    },
});
