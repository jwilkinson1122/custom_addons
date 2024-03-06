/** @odoo-module */

import * as ProductScreen from "@pod_point_of_sale/../tests/tours/helpers/ProductScreenTourMethods";
import * as PaymentScreen from "@pod_point_of_sale/../tests/tours/helpers/PaymentScreenTourMethods";
import * as ReceiptScreen from "@pod_point_of_sale/../tests/tours/helpers/ReceiptScreenTourMethods";
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("FixedTaxNegativeQty", {
    test: true,
    url: "/pos/ui",
    steps: () =>
        [
            ProductScreen.clickHomeCategory(),

            ProductScreen.clickDisplayedProduct("Zero Amount Product"),
            ProductScreen.selectedOrderlineHas("Zero Amount Product", "1.0", "1.0"),
            ProductScreen.pressNumpad("+/-", "1"),
            ProductScreen.selectedOrderlineHas("Zero Amount Product", "-1.0", "-1.0"),

            ProductScreen.clickPayButton(),
            PaymentScreen.clickPaymentMethod("Bank"),
            PaymentScreen.remainingIs("0.00"),
            PaymentScreen.clickValidate(),

            ReceiptScreen.receiptIsThere(),
        ].flat(),
});
