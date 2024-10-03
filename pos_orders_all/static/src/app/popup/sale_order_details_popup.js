/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";

export class SaleOrderDetailPopup extends AbstractAwaitablePopup {
    static template = "pos_orders_all.SaleOrderDetailPopup";

}