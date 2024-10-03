/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductProduct } from "@pos_all_in_one/app/screens/product_screen/product_product/product_product";

export class ProductTemplatePopup extends AbstractAwaitablePopup {
    static components = {ProductProduct};;
    static template = "pos_all_in_one.ProductTemplatePopup";
    static defaultProps = {
       confirmText: _t("Ok"),
        title: "",
        body: "",
    };

    /**
     * @param {Object} props
     * @param {string} props.startingValue
     */
    setup() {
        super.setup();
        this.pos = usePos();
        
    }

    add_product_variant(ev){
        if(this.env.services.pos.config.allow_selected_close == "auto_close"){
            
            this.pos.get_order().add_product(ev);
            this.cancel();

        }else if(this.env.services.pos.config.allow_selected_close == "selected"){
            this.env.services.pos.get_order().add_product(ev);
        }
    }
}