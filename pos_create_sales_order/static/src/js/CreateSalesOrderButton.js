odoo.define('pos_create_sales_order.CreateSalesOrderButton', function(require) {
	'use strict';

	const PosComponent = require('point_of_sale.PosComponent');
	const ProductScreen = require('point_of_sale.ProductScreen');
	const { useListener } = require('web.custom_hooks');
	let core = require('web.core');
	let _t = core._t;
	const Registries = require('point_of_sale.Registries');


	class CreateSalesOrderButton extends PosComponent {
		constructor() {
			super(...arguments);
			useListener('click', this.onClick);
		}
		async onClick(){
			await this.showPopup('SaleCreatePopup');
		}
	}

	CreateSalesOrderButton.template = 'CreateSalesOrderButton';
	ProductScreen.addControlButton({
		component: CreateSalesOrderButton,
		condition: function() {
			return this.env.pos.config.create_sale_order;
		},
	});
	Registries.Component.add(CreateSalesOrderButton);
	return CreateSalesOrderButton;
});