// BiProductList js
odoo.define('podiatry_pos_modifier.BiProductList', function (require) {
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

	const ProductList = require('point_of_sale.ProductList');

	const BiProductList = (ProductList) =>
		class extends ProductList {
			constructor() {
				super(...arguments);
				// this.side_prod_list = []

			}
			closeModifierScreen() {
				var self = this;
				$('.modifiers-list').hide();
				$('.product-list').show();
				$('.products-widget-control').show();
				self.modifier_attribute = [];
				var DeviceRadio = document.querySelector('input[type=radio][name=x]:checked'
				);
				if (DeviceRadio) {
					DeviceRadio.checked = false;
					$('.modifiers-product-list').hide();
					$('#pair').hide();
					$('#single').hide();
					$('#ask').show();
				}
			}

			doneModifier() {
				// self.side_prod_list = []
				$('.modifiers-list').hide();
				$('.side-prod-list').show();
			}

			pair() {
				var self = this;
				$('#pair').show();
				$('#single').hide();
				$('#ask').hide();
				$('#single_device').hide();
				$('.modifiers-product-list').show();
				self.modifier_attribute = [];
			}
			single() {
				var self = this;
				$('#ask').hide();
				$('#single').show();
				$('#single_device').show();
				$('.modifiers-product-list').show();
				$('#pair').hide();
				self.modifier_attribute = [];
				var inSingleRadio = document.querySelector('input[name="single"]:checked'
				);
				if (inSingleRadio) {
					$('.modifiers-product-list').show();
				}
			}

			modifierSelection(event) {
				var self = this;
				var modifier_prod_list = []
				var selected_modifier_id = parseInt(event.currentTarget.dataset['productId'])

				var product = self.env.pos.db.get_product_by_id(selected_modifier_id)

				var checkRadio = document.querySelector('input[name="x"]:checked'
				);

				var option = false;
				var laterality_type = false;
				if (checkRadio.value == "pair") {
					option = "Pair"
					laterality_type = "pair"
				} else if (checkRadio.value == "single") {
					var singleRadio = document.querySelector('input[name="single"]:checked'
					);
					laterality_type = "single"
					if (singleRadio.value == "left") {
						option = "Left";
					} else if (singleRadio.value == "right") {
						option = "Right";
					}
				}

				product['image_url'] = `/web/image?model=product.product&field=image_128&id=${product.id}&write_date=${product.write_date}&unique=1`;
				modifier_prod_list.push(product)
				self.showPopup('ModifierProductPopup', {
					modifier_prod: modifier_prod_list,
					option: option,
					laterality_type: laterality_type,
					modifier_attribute: self.modifier_attribute,
				})
			}

			selectSubProduct() {
				var self = this;
				var order = self.env.pos.get_order();
				var product = order.get_selected_orderline().product;


				if (self.env.pos.side_prod_list.length == 0) {
					self.showPopup('ErrorPopup', {
						title: self.env._t('Side Product'),
						body: self.env._t('Side Products Are Not Define For This Product.'),
					});
				} else {
					$('.side-prod-info').show();
					$('.side-prod-list').hide();
				}
			}

			cancel_add_side_product() {
				$('.side-prod-list').hide();
				$('.product-list').show();
				$('.products-widget-control').show();
				var DeviceRadio = document.querySelector('input[type=radio][name=x]:checked'
				);
				if (DeviceRadio) {
					DeviceRadio.checked = false;
					$('.modifiers-product-list').hide();
					$('#pair').hide();
					$('#single').hide();
					$('#ask').show();
				}
			}

			add_sub_product(event) {
				var self = this;
				var product_id = (event.currentTarget.dataset['productId']);
				var product = self.env.pos.db.get_product_by_id(product_id);
				var order = self.env.pos.get_order();
				var selectedLine = order.get_selected_orderline();


				var vals_list = {};
				var modifier_list = self.modifier_attribute;
				if (product) {
					vals_list.id = product.id;
					vals_list.qty = 1;
					vals_list.display_name = product.display_name;
					vals_list.categ_id = product.categ_id;
					vals_list.image_url = product.image_url;
					vals_list.lst_price = product.lst_price;
					vals_list.name = product.name;
					vals_list.pos_categ_id = product.pos_categ_id;
					vals_list.product_template_attribute_value_ids = product.product_template_attribute_value_ids;
					vals_list.product_tmpl_id = product.product_tmpl_id;
					vals_list.taxes_id = product.taxes_id;
					vals_list.template_name = product.template_name;
					vals_list.uom_id = product.uom_id;
					vals_list.is_sub = true;
				}
				if (modifier_list.length > 0) {
					if (_.findWhere(modifier_list, { id: vals_list.id })) {
						var increase = _.findWhere(modifier_list, { id: vals_list.id })
						increase.qty += 1;
					}
					else {
						modifier_list.push(vals_list)
					}
				}
				else {
					modifier_list.push(vals_list)
				}
				selectedLine.set_modifier(modifier_list)
			}

			doneSubProduct() {
				$('.side-prod-info').hide();
				$('.product-list').show();
				$('.products-widget-control').show();
				var DeviceRadio = document.querySelector('input[type=radio][name=x]:checked'
				);
				if (DeviceRadio) {
					DeviceRadio.checked = false;
					$('.modifiers-product-list').hide();
					$('#pair').hide();
					$('#single').hide();
					$('#ask').show();
				}
			}
		};

	Registries.Component.extend(ProductList, BiProductList);

	return ProductList;

});
