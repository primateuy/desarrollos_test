odoo.define('ateam_adaptations.SetPricelistButtonOverride', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');
    var core = require('web.core');
    var _t = core._t;

    var rpc = require('web.rpc');

    class SetPricelistButtonCustom extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }

        get currentOrder() {
            return this.env.pos.get_order();
        }

        get currentPricelistName() {
            const order = this.currentOrder;
            if(order.pricelist['items'][0]){
            var pricelist_name = order.pricelist['items'][0].pricelist_id[1];
            if (document.querySelector('.control-button.o_pricelist_button')) {
                var default_pricelist = document.querySelector('.control-button.o_pricelist_button').textContent;
                if(default_pricelist != pricelist_name){
                rpc.query({
                    model: 'pos.config',
                    method: 'set_pricelist',
                    args: [[], order.pricelist['items'][0].currency_id[0]],
                }).then(function (result) {
                        window.location.reload();
                });
               }
               }
            }
            return order && order.pricelist
                ? order.pricelist.display_name
                : this.env._t('Pricelist');
        }

        async onClick() {
            // Create the list to be passed to the SelectionPopup.
            // Pricelist object is passed as item in the list because it
            // is the object that will be returned when the popup is confirmed.
            const selectionList = this.env.pos.pricelists.map(pricelist => ({
                id: pricelist.id,
                label: pricelist.name,
                isSelected: pricelist.id === this.currentOrder.pricelist.id,
                item: pricelist,
            }));

            const { confirmed, payload: selectedPricelist } = await this.showPopup(
                'SelectionPopup',
                {
                    title: this.env._t('Select the pricelist'),
                    list: selectionList,
                }
            );

            if (confirmed) {
                this.currentOrder.set_pricelist(selectedPricelist);
            }
        }

}
    SetPricelistButtonCustom.template = 'SetPricelistButtonCustom';

    ProductScreen.addControlButton({
        component: SetPricelistButtonCustom,
        condition: function() {
        debugger;
            if(this.env.pos.pricelists){
                return this.env.pos.config.use_pricelist && this.env.pos.pricelists.length > 1;
            }
        },
        position: ['replace', 'SetPricelistButton']
    });

    Registries.Component.add(SetPricelistButtonCustom);

    return SetPricelistButtonCustom;
});
