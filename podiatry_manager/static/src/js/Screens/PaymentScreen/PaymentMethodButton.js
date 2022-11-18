odoo.define('podiatry_manager.PaymentMethodButton', function(require) {
    'use strict';

    const PosComponent = require('podiatry_manager.PosComponent');
    const Registries = require('podiatry_manager.Registries');

    class PaymentMethodButton extends PosComponent {}
    PaymentMethodButton.template = 'PaymentMethodButton';

    Registries.Component.add(PaymentMethodButton);

    return PaymentMethodButton;
});
