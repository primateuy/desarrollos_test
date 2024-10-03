/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class ProductProduct extends Component {
    static template = "pos_all_in_one.ProductProduct";
    static props = {
        productId: Number,
    };

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }
    get imageUrl() {
        const product = this.props.product;
        return `/web/image?model=product.product&field=image_128&id=${product.id}&write_date=${product.write_date}&unique=1`;
    }
    get pricelist() {
        const current_order = this.env.services.pos.get_order();
        if (current_order) {
            return current_order.pricelist;
        }
        return this.env.services.pos.default_pricelist;
    }
    get price() {
        const formattedUnitPrice = this.env.services.pos.format_currency(
            this.props.product.get_price(this.pricelist, 1),
            'Product Price'
        );
        if (this.props.product.to_weight) {
            return `${formattedUnitPrice}/${
                this.env.services.pos.units_by_id[this.props.product.uom_id[0]].name
            }`;
        } else {
            return formattedUnitPrice;
        }
    }   
}
