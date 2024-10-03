/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";

export class PosConfirmationPopup extends AbstractAwaitablePopup {
    static template = "pos_all_in_one.PosConfirmationPopup";
    static defaultProps = {
        confirmText: _t(""),
        cancelText: _t("Ok"),
        title: _t("Stock Transfer"),
        body: "",
    };

    setup() {
        super.setup();
	}	

	transfer_backend_view() {
	    window.location = '/web?#id='+this.props.transfer_id+'&action=stock.action_picking_tree_all&model=stock.picking&view_type=form&cids=1&menu_id=170';
	}

	cancel() {
        this.props.close({ confirmed: false, payload: null });
    }   
}
