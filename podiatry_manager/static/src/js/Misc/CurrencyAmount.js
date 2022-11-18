odoo.define('podiatry_manager.CurrencyAmount', function(require) {
    'use strict';

    const PosComponent = require('podiatry_manager.PosComponent');
    const Registries = require('podiatry_manager.Registries');

    class CurrencyAmount extends PosComponent {}
    CurrencyAmount.template = 'CurrencyAmount';

    Registries.Component.add(CurrencyAmount);

    return CurrencyAmount;
});
