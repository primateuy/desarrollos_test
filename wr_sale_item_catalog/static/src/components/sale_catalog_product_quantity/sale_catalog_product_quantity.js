/** @odoo-module */

import { registry } from "@web/core/registry";
import { useAutofocus } from "@web/core/utils/hooks";
import { archParseBoolean } from '@web/views/utils';
import { formatFloat } from "@web/views/fields/formatters";
import { FloatField } from '@web/views/fields/float/float_field';

const { useState, useRef, useEffect } = owl;

export class SaleCatalogProductQuantity extends FloatField {
    setup() {
        super.setup(...arguments);
        const refName = 'numpadDecimal';
        useAutofocus({ refName });
        this.state = useState({
            readonly: this.props.readonly,
            addSmallClass: this.props.value.toString().length > 5,
        });

        const ref = useRef(refName);
        useEffect( // remove 0 when the input is focused.
            (el) => {
                if (el) {
                    if (["INPUT", "TEXTAREA"].includes(el.tagName) && el.type === 'number') {
                        el.value = el.value === '0' ? '' : el.value;
                    }
                }
            },
            () => [ref.el]
        );
    }

    get formattedValue() {
        if (!this.state.readonly && this.props.inputType === "number") {
            return this.props.value;
        }
        return formatFloat(this.props.value, { noTrailingZeros: true });
    }

    toggleMode() {
        this.state.readonly = !this.state.readonly;
    }

    setReadonly(readonly) {
        if (this.state.readonly !== readonly) {
            this.toggleMode();
        }
    }

    removeQuantity() {
        this.props.update(this.props.value > 1 ? this.props.value - 1 : 0);
    }

    addQuantity() {
        this.props.update(this.props.value + 1);
    }

    onInput(ev) {
        this.state.addSmallClass = ev.target.value.length > 5;
    }

    /**
     * Handle the keydown event on the input
     *
     * @param {KeyboardEvent} ev
     */
    onKeyDown(ev) {
        if (ev.key === 'Enter') {
            ev.target.dispatchEvent(new Event('change'));
            ev.target.dispatchEvent(new Event('blur'));
        }
    }
}

SaleCatalogProductQuantity.props = {
    ...FloatField.props,
    hideButtons: { type: Boolean, optional: true }
};
SaleCatalogProductQuantity.defaultProps = {
    ...FloatField.defaultProps,
    hideButtons: false,
};

SaleCatalogProductQuantity.template = 'wr_sale_item_catalog.SaleCatalogProductQuantity';
SaleCatalogProductQuantity.extractProps = (props) => {
    return {
        ...FloatField.extractProps(props),
        hideButtons: archParseBoolean(props.attrs.hide_buttons),
    };
};

registry.category('fields').add('sale_catalog_product_quantity', SaleCatalogProductQuantity);
