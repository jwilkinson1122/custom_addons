odoo.define('podiatry_manager.PaymentScreenNumpad', function(require) {
    'use strict';

    const PosComponent = require('podiatry_manager.PosComponent');
    const Registries = require('podiatry_manager.Registries');

    class PaymentScreenNumpad extends PosComponent {
        constructor() {
            super(...arguments);
            this.decimalPoint = this.env._t.database.parameters.decimal_point;
        }
    }
    PaymentScreenNumpad.template = 'PaymentScreenNumpad';

    Registries.Component.add(PaymentScreenNumpad);

    return PaymentScreenNumpad;
});
