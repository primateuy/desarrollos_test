/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PartnerListScreen } from "@point_of_sale/app/screens/partner_list/partner_list";
import { Component, useEffect, useRef, onMounted } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(PartnerListScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
    },

    async showOrders(partner){
        let partner_id = partner.id;
        await this.pos.showScreen('PosOrdersScreen', {
            'selected_partner_id': partner_id,
        });
    }   
});
