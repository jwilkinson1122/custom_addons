
// PodProductScreen js
odoo.define('pod_pos.PodProductScreen', function (require) {
	"use strict";

	const models = require('point_of_sale.models');
	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const Session = require('web.Session');
	const chrome = require('point_of_sale.Chrome');
	const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
	const NumberBuffer = require('point_of_sale.NumberBuffer');
	const { useListener } = require('web.custom_hooks');
	const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
	const { useState } = owl.hooks;

	const ProductScreen = require('point_of_sale.ProductScreen');

	const PodProductScreen = (ProductScreen) =>
		class extends ProductScreen {
			constructor() {
				super(...arguments);

			}
			async _clickProduct(event) {
				var self = this;
				const product = event.detail;
				if (product.product_variant_count > 1) {
					var prod_template = this.env.pos.db.product_template_by_id[product.product_tmpl_id];
					var prod_list = [];
					prod_template.product_variant_ids.forEach(function (prod) {
						prod_list.push(self.env.pos.db.get_product_by_id(prod));
					});
					// this.product_template_list_widget.set_product_list(prod_list);

					this.showPopup('ProductTemplatePopupWidget', { 'variant_ids': prod_list });
				} else {
					if (product.to_weight && this.env.pos.config.iface_electronic_scale) {
						this.showScreen('scale', { product: product });
					} else {
						this.env.pos.get_order().add_product
					}
					super._clickProduct(event);
				}
			}

			_setValue(val) {
				if (this.currentOrder.get_selected_orderline()) {
					if (this.state.numpadMode === 'quantity') {
						const result = this.currentOrder.get_selected_orderline().set_quantity(val);

						if (val == 'remove') {
							$('.modifiers-list').hide();

							$('.product-list').show();
							$('.products-widget-control').show();
							self.modifier_attribute = [];

							var OrthoticRadio = document.querySelector(
								'input[type=radio][name=x]:checked'
							);
							if (OrthoticRadio) {
								OrthoticRadio.checked = false;
								$('.modifiers-product-list').hide();
								$('#pair_orthotic').hide();
								$('#single_orthotic').hide();
								$('#ask').show();
							}
						}
						if (!result) NumberBuffer.reset();
					} else if (this.state.numpadMode === 'discount') {
						this.currentOrder.get_selected_orderline().set_discount(val);
					} else if (this.state.numpadMode === 'price') {
						var selected_orderline = this.currentOrder.get_selected_orderline();
						selected_orderline.price_manually_set = true;
						selected_orderline.set_unit_price(val);
					}
					if (this.env.pos.config.iface_customer_facing_display) {
						this.env.pos.send_current_order_to_customer_facing_display();
					}
				}
			}
		};

	Registries.Component.extend(ProductScreen, PodProductScreen);

	return ProductScreen;

});
