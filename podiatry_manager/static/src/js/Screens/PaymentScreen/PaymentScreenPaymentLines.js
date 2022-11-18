odoo.define('podiatry_manager.PaymentScreenPaymentLines', function(require) {
    'use strict';

    const PosComponent = require('podiatry_manager.PosComponent');
    const Registries = require('podiatry_manager.Registries');

    class PaymentScreenPaymentLines extends PosComponent {
        formatLineAmount(paymentline) {
            return this.env.pos.format_currency_no_symbol(paymentline.get_amount());
        }
        selectedLineClass(line) {
            return { 'payment-terminal': line.get_payment_status() };
        }
        unselectedLineClass(line) {
            return {};
        }
    }
    PaymentScreenPaymentLines.template = 'PaymentScreenPaymentLines';

    Registries.Component.add(PaymentScreenPaymentLines);

    return PaymentScreenPaymentLines;
});
