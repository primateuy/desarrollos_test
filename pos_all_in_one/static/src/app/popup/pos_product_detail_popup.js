/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { ProductDetailsEditPopup } from "@pos_all_in_one/app/popup/product_details_edit_popup";


export class PosProductDetailPopup extends AbstractAwaitablePopup {
    static template = "pos_all_in_one.PosProductDetailPopup";

    setup() {
        super.setup();
        this.order = this.props.order;
        this.pos = usePos();
    }

    get productImageUrl() {
        const product = this.props.order;
        if (product.id) {
            return `/web/image?model=product.product&field=image_512&id=${product.id}&unique=${product.__last_update}`;
        } else {
            return false;
        }
    }

    async uploadImage(event) {
        let self = this;
        const file = event.target.files[0];
        if (file) {
            if (!file.type.match(/image.*/)) {
                await this.pos.popup.add(ErrorPopup, {
                    title: _t('Unsupported File Format'),
                    body: _t(
                        'Only web-compatible Image formats such as .png or .jpeg are supported.'
                    ),
                });
            } else {
                const imageUrl = await getDataURLFromFile(file);
                const loadedImage = await this._loadImage(imageUrl);
                if (loadedImage) {
                    const resizedImage = await this._resizeImage(loadedImage, 800, 600);
                    this.changes.image_1920 = resizedImage.toDataURL();
                    // Rerender to reflect the changes in the screen
                    this.render();
                }
            }
        }

    }
    _resizeImage(img, maxwidth, maxheight) {
        var canvas = document.createElement('canvas');
        var ctx = canvas.getContext('2d');
        var ratio = 1;

        if (img.width > maxwidth) {
            ratio = maxwidth / img.width;
        }
        if (img.height * ratio > maxheight) {
            ratio = maxheight / img.height;
        }
        var width = Math.floor(img.width * ratio);
        var height = Math.floor(img.height * ratio);

        canvas.width = width;
        canvas.height = height;
        ctx.drawImage(img, 0, 0, width, height);
        return canvas;
    }
        
    _loadImage(url) {
        let self = this;
        return new Promise((resolve) => {
            const img = new Image();
            img.addEventListener('load', () => resolve(img));
            img.addEventListener('error', () => {
                this.pos.popup.add(ErrorPopup, {
                    title: _t('Loading Image Error'),
                    body: _t(
                        'Encountered error when loading image. Please try again.'
                    ),
                });
                resolve(false);
            });
            img.src = url;
        });
    }


    edit_product() {
        this.pos.popup.add(ProductDetailsEditPopup, {
            'product': this.order,
        });
        this.cancel();
    }

}