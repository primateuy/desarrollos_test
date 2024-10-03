/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class PosBagPopup extends AbstractAwaitablePopup {
    static template = "pos_orders_all.PosBagPopup";

    setup() {
        this.pos = usePos();
    }

    go_back_screen() {
        this.showScreen('ProductScreen');
        this.env.posbus.trigger('close-popup', {
            popupId: this.props.id });
    }

    get bags() {
        let bags = [];
        $.each(this.props.products, function( i, prd ){
            prd['bag_image_url'] = `/web/image?model=product.product&field=image_128&id=${prd.id}&write_date=${prd.write_date}&unique=1`;
            bags.push(prd)
        });
        return bags;
    }
    
    click_on_bag_product(event) {
        var self = this;
        var bag_id = parseInt(event.currentTarget.dataset['productId'])
        this.pos.addProductToCurrentOrder(this.pos.db.product_by_id[bag_id])
        this.pos.showScreen('ProductScreen');
        this.props.close({ confirmed: false, payload: false });
    }
}
