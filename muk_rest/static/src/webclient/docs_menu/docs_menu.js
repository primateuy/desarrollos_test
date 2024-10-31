/** @odoo-module **/

import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";

const { Component, useState, onWillStart, useExternalListener } = owl;

export class DocsMenu extends Component {
	setup() {
        this.docsService = useService('rest_docs');
        this.state = useState({ open: false });
        onWillStart(async () => {
            this.hasAccess = await this.docsService.checkAccess();
        });
        useExternalListener(
        	window, 'click', this.onWindowClicked
        );
    }
	onWindowClicked(ev) {
		if (this.state.open) {
			this.state.open = false;
		}
	}
}

DocsMenu.template = 'muk_rest.DocsMenu';
DocsMenu.toggleDelay = 1000;

export const systrayItem = {
    Component: DocsMenu,
    isDisplayed(env) {
        return env.debug && !env.isSmall;
    },
};

registry.category('systray').add(
	'DocsMenu', systrayItem, { sequence: 75 }
);
