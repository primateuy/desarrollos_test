/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { getDataURLFromFile } from "@web/core/utils/urls";
import { useService } from "@web/core/utils/hooks";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { Order, Product } from "@point_of_sale/app/store/models";
const { onMounted } = owl;

export class ProductDetailsCreatePopup extends AbstractAwaitablePopup {
	static template = "pos_all_in_one.ProductDetailsCreatePopup";
	static defaultProps = {
		confirmText: 'Create',
		cancelText: 'Close',
		title: 'Create Product',
		body: '',
	};

	setup() {
		super.setup();
		this.changes = {};
		this.pos = usePos();
		this.orm = useService("orm");
		onMounted(() => this._mounted());
	}

	syncProdData(notifications) {
		let self = this;
		notifications.forEach(function(ntf) {
			ntf = JSON.parse(JSON.stringify(ntf))
			if (ntf && ntf.type && ntf.type == "product.product/sync_data") {
				let prod = ntf.payload.product[0];
				let old_category_id = self.pos.db.product_by_id[prod.id];
				let new_category_id = prod.bi_pos_reports_catrgory;
				let stored_categories = self.pos.db.product_by_category_id;

				prod.pos = self.pos;
				if (self.pos.db.product_by_id[prod.id]) {
					if (old_category_id.pos_categ_id) {
						stored_categories[old_category_id.pos_categ_id[0]] = stored_categories[old_category_id.pos_categ_id[0]].filter(function(item) {
							return item != prod.id;
						});
					}
					if (stored_categories[new_category_id]) {
						stored_categories[new_category_id].push(prod.id);
					}
					let updated_prod = self.updateProd(prod);
				} else {
					let updated_prod = self.updateProd(prod);
				}
			}
		});
		self.pos.is_sync = true;
	}

	updateProd(product) {
		let self = this;
		self.pos._loadProductProduct([product]);
		const productMap = {};
		const productTemplateMap = {};

		product.pos = self.pos;
		product.applicablePricelistItems = {};
		productMap[product.id] = product;
		productTemplateMap[product.product_tmpl_id[0]] = (productTemplateMap[product.product_tmpl_id[0]] || []).concat(product);
		let new_prod = new Product(product);
		for (let pricelist of self.pos.pricelists) {
			for (const pricelistItem of pricelist.items) {
				if (pricelistItem.product_id) {
					let product_id = pricelistItem.product_id[0];
					let correspondingProduct = productMap[product_id];
					if (correspondingProduct) {
						self.pos._assignApplicableItems(pricelist, correspondingProduct, pricelistItem);
					}
				} else if (pricelistItem.product_tmpl_id) {
					let product_tmpl_id = pricelistItem.product_tmpl_id[0];
					let correspondingProducts = productTemplateMap[product_tmpl_id];
					for (let correspondingProduct of(correspondingProducts || [])) {
						self.pos._assignApplicableItems(pricelist, correspondingProduct, pricelistItem);
					}
				} else {
					for (const correspondingProduct of product) {
						self.pos._assignApplicableItems(pricelist, correspondingProduct, pricelistItem);
					}
				}
			}
		}
		self.pos.db.product_by_id[product.id] = new_prod;
	}

	get is_sync() {
		return this.pos.is_sync;
	}
	
	_mounted() {
		var self = this;
		self.env.services['bus_service'].addEventListener('notification', ({ detail: notifications }) => {
			self.syncProdData(notifications);
		});
	}

	captureChange(event) {
		this.changes[event.target.name] = event.target.value;
	}

	get partnerImageUrl() {
		// We prioritize image_1920 in the `changes` field because we want
		// to show the uploaded image without fetching new data from the server.
		const product = this.props.products;
		if (this.changes.image_1920) {
			return this.changes.image_1920;
		} else if (product.id) {
			return `/web/image?model=product.product&id=${product.id}&field=image_128&write_date=${product.write_date}&unique=${product.__last_update}`;
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

	async create_product() {
		var self = this;
		var fields = {};
		$('.basic_info .detail').each(function(idx, el) {
			fields[el.name] = el.value;
		})
		$('.advance_info .detail').each(function(idx, el) {
			fields[el.name] = el.value;
		})

		if (fields.display_name == false) {
			self.pos.popup.add(ErrorPopup, {
				title: _t('Error: Could not Save Changes'),
				body: _t('please enter product details.'),
			});
		} else {
			fields.id = false;
			fields.image_1920 = this.changes.image_1920
			fields.pos_categ_id = fields.pos_categ_id || false;
			fields.list_price = fields.list_price || '';
			fields.categ_id = fields.categ_id || '';
			fields.detailed_type = fields.product_type || false;
			fields.barcode = fields.barcode || false;
			var taxes = $.map($('.product_tax:checked'), function(c) { return parseInt(c.value); });
			fields.taxes = taxes || false;
			if (fields.cost_price == '') {
				fields.cost_price = '0'
			}
			if (fields.list_price == '') {
				fields.list_price = '0'
			}
			if (fields.categ_id == '') {
				fields.categ_id = '1'
			}
			await self.orm.call(
				'product.product',
				'create_from_ui',
				[fields],
			).then(function(product) {
				var domain = [
					['id', '=', product]
				];
				self.orm.searchRead(
					'product.product',
					domain,
					["id","name"]
					
				).then(function(out) {
					out = out[0];
					out.pos = self.pos;
					let final_prd = self.pos.db.get_product_by_id(out.id);
					if(final_prd){
						final_prd.taxes_id = taxes;
					}
				});
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

	async create_product_add_product() {
		var self = this;
		var fields = {};
		$('.basic_info .detail').each(function(idx, el) {
			fields[el.name] = el.value;
		})
		$('.advance_info .detail').each(function(idx, el) {
			fields[el.name] = el.value;
		})

		if (fields.display_name == false) {
			self.pos.popup.add(ErrorPopup, {
				title: _t('Error: Could not Save Changes'),
				body: _t('please enter product details.'),
			});
		} else {
			fields.id = false;
			fields.image_1920 = this.changes.image_1920
			fields.pos_categ_id = fields.pos_categ_id || false;
			fields.list_price = fields.list_price || '';
			fields.categ_id = fields.categ_id || '';
			fields.detailed_type = fields.product_type || false;
			fields.barcode = fields.barcode || false;
			var taxes = $.map($('.product_tax:checked'), function(c) { return parseInt(c.value); });
			fields.taxes = taxes || false;
			if (fields.cost_price == '') {
				fields.cost_price = '0'
			}
			if (fields.list_price == '') {
				fields.list_price = '0'
			}
			if (fields.categ_id == '') {
				fields.categ_id = '1'
			}

			await self.orm.call(
				'product.product',
				'create_from_ui',
				[fields],
			).then(async function(product) {
				let domain = [['id','=',product]];
				self.orm.searchRead(
					'product.product',
					domain,
					["id","name"]
					
				).then(function(out) {
					out = out[0];
					out.pos = self.pos;
					let final_prd = self.pos.db.get_product_by_id(out.id);
					if(final_prd){
						final_prd.taxes_id = taxes;
						let selectedOrder = self.pos.get_order();
						selectedOrder.add_product(final_prd, { 'quantity': 1, });
					}
					self.pos.is_sync = true;
					alert('Product Details Saved!!!!');
					self.props.close({ confirmed: true, payload: null });
					self.pos.closeTempScreen();
					self.pos.showScreen('ProductScreen', {});
				});

				
			}, function(err, event) {
				self.pos.popup.add(ErrorPopup, {
					title: _t('Error: Could not Save Changes'),
					body: _t('Added Product Details getting Error.'),
				});
			});
		}
	}

}
