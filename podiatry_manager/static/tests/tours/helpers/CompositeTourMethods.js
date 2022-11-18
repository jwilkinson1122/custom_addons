odoo.define('podiatry_manager.tour.CompositeTourMethods', function (require) {
    'use strict';

    const { ProductScreen } = require('podiatry_manager.tour.ProductScreenTourMethods');
    const { ReceiptScreen } = require('podiatry_manager.tour.ReceiptScreenTourMethods');
    const { PaymentScreen } = require('podiatry_manager.tour.PaymentScreenTourMethods');
    const { ClientListScreen } = require('podiatry_manager.tour.ClientListScreenTourMethods');

    function makeFullOrder({ orderlist, customer, payment, ntimes = 1 , customerNote}) {
        for (let i = 0; i < ntimes; i++) {
            ProductScreen.exec.addMultiOrderlines(...orderlist);
            if (customer) {
                ProductScreen.do.clickCustomerButton();
                ClientListScreen.exec.setClient(customer);
            }
            if (customerNote) { // this will add a note to the last selected order line
                ProductScreen.exec.addCustomerNote(customerNote);
            }
            ProductScreen.do.clickPayButton();
            PaymentScreen.exec.pay(...payment);
            ReceiptScreen.exec.nextOrder();
        }
    }

    return { makeFullOrder };
});
