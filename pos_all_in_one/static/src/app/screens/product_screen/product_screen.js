/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
const { onMounted } = owl;
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(ProductScreen.prototype, {
    setup() {
        super.setup();
        this.pos = usePos();
        this.show_buttons = true;
        // onMounted(() => this._mounted());
    },

    // _mounted() {
    //     if(this.show_buttons){
    //         $('.control-button').show();
    //     }else{
    //         $('.control-button').hide();
    //     }
    // },

    _onClickHideButtons(event){
        this.show_buttons = ! this.show_buttons ;
        if(this.show_buttons){
            $('.control-button').show();
        }else{
            $('.control-button').hide();
        }
        this.render();
    },

    getNumpadButtons() {
        var allow_numpad = true;
        var allow_qty = true;
        var allow_discount = true;
        var edit_price = true;
        var allow_plus_minus_button = true;
        var allow_remove_orderline = true;
        var cashier = this.pos.get_cashier();
        if(cashier.id){
            allow_numpad = cashier.is_allow_numpad;
            allow_qty = cashier.is_allow_qty;
            allow_discount = cashier.is_allow_discount;
            edit_price = cashier.is_edit_price;
            allow_plus_minus_button = cashier.is_allow_plus_minus_button;
            allow_remove_orderline = cashier.is_allow_remove_orderline;
        }
        return [
            { value: "1" , disabled: !allow_numpad},
            { value: "2" , disabled: !allow_numpad},
            { value: "3" , disabled: !allow_numpad},
            { value: "quantity", text: "Qty" , disabled: !allow_qty},
            { value: "4" , disabled: !allow_numpad},
            { value: "5" , disabled: !allow_numpad},
            { value: "6" , disabled: !allow_numpad},
            { value: "discount", text: "% Disc", disabled: !this.pos.config.manual_discount ||  !allow_discount },
            { value: "7" , disabled: !allow_numpad},
            { value: "8" , disabled: !allow_numpad},
            { value: "9" , disabled: !allow_numpad},
            { value: "price", text: "Price", disabled: !this.pos.cashierHasPriceControlRights() || !edit_price },
            { value: "-", text: "+/-" , disabled: !allow_plus_minus_button},
            { value: "0" , disabled: !allow_numpad},
            { value: this.env.services.localization.decimalPoint , disabled: !allow_numpad},
            // Unicode: https://www.compart.com/en/unicode/U+232B
            { value: "Backspace", text: "⌫" , disabled: !allow_remove_orderline},
        ].map((button) => ({
            ...button,
            class: this.pos.numpadMode === button.value ? "active border-primary" : "",
        }));
    }
});
