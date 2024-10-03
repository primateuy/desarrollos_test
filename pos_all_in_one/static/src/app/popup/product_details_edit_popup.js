/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { getDataURLFromFile } from "@web/core/utils/urls";
import { useService } from "@web/core/utils/hooks";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
// import { PosProductScreen } from "@pos_all_in_one/app/screens/product_screen/pos_product_screen/pos_product_screen";

export class ProductDetailsEditPopup extends AbstractAwaitablePopup {
    static template = "pos_all_in_one.ProductDetailsEditPopup";
    static defaultProps = {
        confirmText: _t("Ok"),
        cancelKey: false,
        body: "",
    };

    setup() {
        super.setup();
        this.changes = {}
        this.pos = usePos();
        this.orm = useService("orm");
        this.product = this.props.product;
    }

    captureChange(event) {
        this.changes[event.target.name] = event.target.value;
    }
    get productImageUrl() {
        const product = this.props.product;
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
        /**
         * Loading image is converted to a Promise to allow await when
         * loading an image. It resolves to the loaded image if succesful,
         * else, resolves to false.
         *
         * [Source](https://stackoverflow.com/questions/45788934/how-to-turn-this-callback-into-a-promise-using-async-await)
         */
    _loadImage(url) {
        let self = this;
        return new Promise((resolve) => {
            const img = new Image();
            img.addEventListener('load', () => resolve(img));
            img.addEventListener('error', () => {
                this.pos.popup.add(ErrorPopup, {
                    title: self.env._t('Loading Image Error'),
                    body: self.env._t(
                        'Encountered error when loading image. Please try again.'
                    ),
                });
                resolve(false);
            });
            img.src = url;
        });
    }


    save_product() {
        var self = this;
        var fields = {};

        $('.partner-details-box .detail').each(function(idx, el) {
            fields[el.name] = el.value;
        });
        
        if (fields.display_name == false || fields.pos_categ_ids == false) {
            self.pos.popup.add(ErrorPopup, {
                'title': _t('Error: Could not Save Changes'),
                'body': _t('Please Enter Product Details.'),
            });
        } else {
            if (this.product != false) {
                fields.id = this.product.id || false;
            } else {
                fields.id = false;
            }
            fields.image_1920 = this.changes.image_1920
            fields.pos_categ_ids = parseFloat(fields.pos_categ_ids) || false;
            fields.list_price = parseFloat(fields.list_price) || '';
            fields.cost_price = parseFloat(fields.cost_price) || '';
            fields.barcode = parseInt(fields.barcode) || false;
            if (fields.cost_price == '') {
                fields.cost_price = 0
            }
            if (fields.list_price == '') {
                fields.list_price = 0
            }

            let productId = self.orm.call(
               'product.product',
                'create_from_ui',
                [fields],
            )
            .then(function(product_id) {
                self.pos.is_sync = true;
                alert('Product Details Saved!!!!');
                self.pos.showScreen('ProductScreen', {});
                self.cancel();
            }, function(err, event) {
                self.pos.popup.add(ErrorPopup, {
                    title: _t('Error: Could not Save Changes'),
                    body: _t('Added Product Details getting Error.'),
                });
            });
        }
    }    
}
