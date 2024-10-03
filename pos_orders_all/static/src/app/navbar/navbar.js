/** @odoo-module */

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
// import { ProductLowStock } from "@pos_orders_all/app/screens/product_screen/product_low_stock_screen/product_low_stock_screen";

patch(Navbar.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        this.orm = useService("orm");
    },

    async show_products(){
        var self = this;
        let low_stock=self.pos.config.low_stock
        await this.orm.call(
            "product.product",
            "get_low_stock_products",
            [0,low_stock],
            ).then(function(data) {
                self.pos.low_stock_products = [];
                for(var k=0;k<data.length;k++){
                    let product= self.pos.db.get_product_by_id(data[k]);
                    if (product){
                        self.pos.low_stock_products.push(product);
                    }
                }
                self.pos.showTempScreen('LowStockProducts');
            }
        );
    },
});
