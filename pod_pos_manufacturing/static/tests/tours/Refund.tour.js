/** @odoo-module */

import * as ProductScreenPos from "@point_of_sale/../tests/tours/helpers/ProductScreenTourMethods";
import * as ProductScreenResto from "@pod_pos_manufacturing/../tests/tours/helpers/ProductScreenTourMethods";
const ProductScreen = { ...ProductScreenPos, ...ProductScreenResto };
import * as PaymentScreen from "@point_of_sale/../tests/tours/helpers/PaymentScreenTourMethods";
import * as ReceiptScreen from "@point_of_sale/../tests/tours/helpers/ReceiptScreenTourMethods";
import * as FloorScreen from "@pod_pos_manufacturing/../tests/tours/helpers/FloorScreenTourMethods";
import * as TicketScreen from "@point_of_sale/../tests/tours/helpers/TicketScreenTourMethods";
import * as Order from "@point_of_sale/../tests/tours/helpers/generic_components/OrderWidgetMethods";
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("RefundStayCurrentSectionTour", {
    test: true,
    url: "/pos/ui",
    steps: () =>
        [
            ProductScreen.confirmOpeningPopup(),

            // Create first order and pay it
            FloorScreen.clickSection("2"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ProductScreen.selectedOrderlineHas("Coca-Cola"),
            ProductScreen.clickDisplayedProduct("Coca-Cola"),
            ProductScreen.selectedOrderlineHas("Coca-Cola"),
            ProductScreen.clickDisplayedProduct("Water"),
            ProductScreen.selectedOrderlineHas("Water"),
            ProductScreen.totalAmountIs("6.60"),
            ProductScreen.clickPayButton(),
            PaymentScreen.clickPaymentMethod("Cash"),
            PaymentScreen.clickValidate(),
            ReceiptScreen.clickNextOrder(),

            // Go to another section and refund one of the products
            FloorScreen.clickSection("4"),
            ProductScreen.orderIsEmpty(),
            ProductScreen.clickRefund(),
            TicketScreen.selectOrder("-0001"),
            Order.hasLine({
                productName: "Coca-Cola",
            }),
            ProductScreen.pressNumpad("2"),
            TicketScreen.toRefundTextContains("To Refund: 2.00"),
            TicketScreen.confirmRefund(),
            ProductScreen.isShown(),
            ProductScreen.selectedOrderlineHas("Coca-Cola"),
            ProductScreen.totalAmountIs("-4.40"),
        ].flat(),
});
