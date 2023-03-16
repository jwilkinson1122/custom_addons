odoo.define('point_of_sale.OrderReceiptA4', function (require) {
    'use strict';

    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const Registries = require('point_of_sale.Registries');

    class OrderReceiptA4 extends OrderReceipt {
        constructor() {
            super(...arguments);
        }
    }

    OrderReceiptA4.template = 'OrderReceiptA4';

    Registries.Component.add(OrderReceiptA4);

    return OrderReceiptA4;
});
