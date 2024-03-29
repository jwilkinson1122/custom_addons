
odoo.define('pod_order_management.pos_customer_favorites', function (require) {
	"use strict";
	var models = require('point_of_sale.models');
	var SuperOrder = models.Order;
	const ProductScreen = require('point_of_sale.ProductScreen');
	const Registries = require('point_of_sale.Registries');
	const ClientListScreen = require('point_of_sale.ClientListScreen');
	const ProductsWidgetControlPanel = require('point_of_sale.ProductsWidgetControlPanel');
	const ProductsWidget = require('point_of_sale.ProductsWidget');
	const PaymentScreen = require('point_of_sale.PaymentScreen');

	models.load_models([{
		model: 'customer.favorite.product',
		field: ['product_id', 'partner_id'],
		domain: [],
		loaded: function (self, result) {
			self.db.favorite_item_by_customer = {};
			result.forEach(element => {
				if (self.db.favorite_item_by_customer[element.partner_id[0]])
					self.db.favorite_item_by_customer[element.partner_id[0]].push(element.product_id[0])
				else
					self.db.favorite_item_by_customer[element.partner_id[0]] = [element.product_id[0]]
			});
		}
	}]);

	// Inherit ProductsWidget----------------
	const PosResProductsWidget = (ProductsWidget) =>
		class extends ProductsWidget {
			get productsToDisplay() {
				var self = this;
				var order = self.env.pos.get_order();
				if (order && order.get_client()) {
					$('.customer_favorites').show();
					if (order.show_customer_favorite_list) {
						$('.diselect_fav').hide();
						$('.select_fav').show();
					} else {
						$('.diselect_fav').show();
						$('.select_fav').hide();
					}
				} else {
					$('.customer_favorites').hide();
				}
				if (this.searchWord !== '') {
					var data = this.env.pos.db.search_product_in_category(
						this.selectedCategoryId,
						this.searchWord
					);
					// Filter Fav Products
					if (order && order.show_customer_favorite_list && order.get_client()) {
						$('.select_fav').show();
						$('.diselect_fav').hide();
						var client_favorite_list = self.env.pos.db.favorite_item_by_customer[order.get_client().id]
						var product_list = data
						if (client_favorite_list) {
							product_list = data.filter(element => {
								return client_favorite_list.indexOf(element.id) == -1 ? 0 : 1
							});
						} else {
							product_list = [];
						}
						return product_list
					}
					return data
				} else {
					var data1 = this.env.pos.db.get_product_by_category(this.selectedCategoryId);
					// Filter Fav Products
					if (order && order.show_customer_favorite_list && order.get_client()) {
						$('.select_fav').show();
						$('.diselect_fav').hide();
						var client_favorite_list = self.env.pos.db.favorite_item_by_customer[order.get_client().id]
						var product_list = data1
						if (client_favorite_list) {
							product_list = data1.filter(element => {
								return client_favorite_list.indexOf(element.id) == -1 ? 0 : 1
							});
						} else {
							product_list = [];
						}
						return product_list
					}
					return data1
				}
			}
		};
	Registries.Component.extend(ProductsWidget, PosResProductsWidget);

	models.Order = models.Order.extend({
		initialize: function (attributes, options) {
			self = this;
			self.show_customer_favorite_list = false;
			SuperOrder.prototype.initialize.call(this, attributes, options);
		},
	});

	// Inherit ProductsWidgetControlPanel----------------
	const PosResProductsWidgetControlPanel = (ProductsWidgetControlPanel) =>
		class extends ProductsWidgetControlPanel {
			toggle_customer_fav_list(event) {
				var self = this;
				var order = self.env.pos.get_order();
				setTimeout(function () {
					$('.select_fav').show();
					$('.diselect_fav').hide();
					if (order && order.get_client()) {
						if (order.show_customer_favorite_list) {
							order.show_customer_favorite_list = false;
							self.showScreen('ClientListScreen')
							self.showScreen('ProductScreen')
							$('.diselect_fav').show();
							$('.select_fav').hide();
						} else {
							order.show_customer_favorite_list = true;
							self.showScreen('ClientListScreen')
							self.showScreen('ProductScreen')
						}
					}
				}, 100);
			}
		};
	Registries.Component.extend(ProductsWidgetControlPanel, PosResProductsWidgetControlPanel);

	// Inherit ProductScreen----------------
	const PosResProductScreen = (ProductScreen) =>
		class extends ProductScreen {
			constructor() {
				super(...arguments);
				var self = this;
				var order = self.env.pos.get_order();
				setTimeout(function () {
					if (order && order.get_client()) {
						$('.customer_favorites').show();
						if (order.show_customer_favorite_list) {
							$('.diselect_fav').hide();
							$('.select_fav').show();
						} else {
							$('.diselect_fav').show();
							$('.select_fav').hide();
						}
					} else {
						$('.customer_favorites').hide();
					}
				}, 100);
			}
		};
	Registries.Component.extend(ProductScreen, PosResProductScreen);

	// Inherit ClientListScreen----------------
	const PosResClientListScreen = (ClientListScreen) =>
		class extends ClientListScreen {
			clickClient(event) {
				super.clickClient(event);
				if (this.state.selectedClient) {
					$('.button.show_customer_favorite').show();
				} else {
					$('.button.show_customer_favorite').hide();
				}
			}
			show_customer_favorite(event) {
				var self = this;
				var order = self.env.pos.get_order();
				self.click_favorite = true;
				if (order) {
					order.show_customer_favorite_list = true;
					self.back();
				}
			}
		};
	Registries.Component.extend(ClientListScreen, PosResClientListScreen);

	// Inherit PaymentScreen----------------
	const PosResPaymentScreen = (PaymentScreen) =>
		class extends PaymentScreen {
			async _finalizeValidation() {
				var self = this;
				super._finalizeValidation();
				var order = self.env.pos.get_order();
				var client = order.get_client();
				if (client) {
					order.get_orderlines().forEach(element => {
						if (self.env.pos.db.favorite_item_by_customer[client.id])
							self.env.pos.db.favorite_item_by_customer[client.id].push(element.product.id);
						else
							self.env.pos.db.favorite_item_by_customer[client.id] = [element.product.id];
					});
				}
			}
		};
	Registries.Component.extend(PaymentScreen, PosResPaymentScreen);
});
