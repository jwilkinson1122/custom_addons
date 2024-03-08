
odoo.define("pod_point_of_sale.tour.PosOrderToSaleOrderTour",[], function (require) {
    "use strict";

    const Tour = require("web_tour.tour");

    var steps = [
        {
            content: "Test pod_point_of_sale: Waiting for loading to finish",
            trigger: "body:not(:has(.loader))",
            // eslint-disable-next-line no-empty-function
            run: () => {},
        },
        {
            content: "Test pod_point_of_sale: Close Opening cashbox popup",
            trigger: "div.opening-cash-control .button:contains('Open session')",
        },
        {
            content:
                "Test pod_point_of_sale: Leave category displayed by default",
            trigger: ".breadcrumb-home",
            // eslint-disable-next-line no-empty-function
            run: () => {},
        },
        {
            content:
                "Test pod_point_of_sale: Order a 'Whiteboard Pen' (price 3.20)",
            trigger: ".product-list .product-name:contains('Whiteboard Pen')",
        },
        {
            content: "Test pod_point_of_sale: Click on 'Customer' Button",
            trigger: "button.set-partner",
        },
        {
            content: "Test pod_point_of_sale: Select a customer 'Addison Olson'",
            trigger: "tr.partner-line td div:contains('Addison Olson')",
        },
        {
            content: "Test pod_point_of_sale: Click on 'Create Order' Button",
            trigger: "span.control-button span:contains('Create Order')",
        },
        {
            content:
                "Test pod_point_of_sale: Click on 'Create invoiced order' Button",
            trigger:
                "div.button-sale-order span:contains('Create Invoiced Sale Order')",
        },
        {
            content: "Test pod_point_of_sale: Close the Point of Sale frontend",
            trigger: ".header-button",
        },
        {
            content: "Test pod_point_of_sale: Confirm closing the frontend",
            trigger: ".header-button",
            // eslint-disable-next-line no-empty-function
            run: () => {},
        },
    ];

    Tour.register("PosOrderToSaleOrderTour", {test: true, url: "/pos/ui"}, steps);
});

/* */
