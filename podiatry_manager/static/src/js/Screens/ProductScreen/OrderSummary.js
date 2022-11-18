odoo.define('podiatry_manager.OrderSummary', function(require) {
    'use strict';

    const PosComponent = require('podiatry_manager.PosComponent');
    const Registries = require('podiatry_manager.Registries');

    class OrderSummary extends PosComponent {}
    OrderSummary.template = 'OrderSummary';

    Registries.Component.add(OrderSummary);

    return OrderSummary;
});
