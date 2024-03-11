/** @odoo-module */

import * as PaymentScreen from "@point_of_sale/../tests/tours/helpers/PaymentScreenTourMethods";
import * as ReceiptScreen from "@point_of_sale/../tests/tours/helpers/ReceiptScreenTourMethods";
import * as Chrome from "@point_of_sale/../tests/tours/helpers/ChromeTourMethods";
import * as FloorScreen from "@pos_shop/../tests/tours/helpers/FloorScreenTourMethods";
import * as Order from "@point_of_sale/../tests/tours/helpers/generic_components/OrderWidgetMethods";
import * as ProductScreenPos from "@point_of_sale/../tests/tours/helpers/ProductScreenTourMethods";
import * as ProductScreenResto from "@pos_shop/../tests/tours/helpers/ProductScreenTourMethods";
const ProductScreen = { ...ProductScreenPos, ...ProductScreenResto };
import * as SplitInvoiceScreen from "@pos_shop/../tests/tours/helpers/SplitInvoiceScreenTourMethods";
import * as TicketScreen from "@point_of_sale/../tests/tours/helpers/TicketScreenTourMethods";
import * as combo from "@point_of_sale/../tests/tours/helpers/ComboPopupMethods";
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("SplitInvoiceScreenTour", {
    test: true,
    url: "/pos/ui",
    steps: () =>
        [
            ProductScreen.confirmOpeningPopup(),
            FloorScreen.clickSection("2"),
            ProductScreen.addOrderline("Water", "5", "2", "10.0"),
            ProductScreen.addOrderline("Minute Maid", "3", "2", "6.0"),
            ProductScreen.addOrderline("Coca-Cola", "1", "2", "2.0"),
            ProductScreen.clickSplitInvoiceButton(),

            // Check if the screen contains all the orderlines
            SplitInvoiceScreen.orderlineHas("Water", "5", "0"),
            SplitInvoiceScreen.orderlineHas("Minute Maid", "3", "0"),
            SplitInvoiceScreen.orderlineHas("Coca-Cola", "1", "0"),

            // split 3 water and 1 coca-cola
            SplitInvoiceScreen.clickOrderline("Water"),
            SplitInvoiceScreen.orderlineHas("Water", "5", "1"),
            SplitInvoiceScreen.clickOrderline("Water"),
            SplitInvoiceScreen.clickOrderline("Water"),
            SplitInvoiceScreen.orderlineHas("Water", "5", "3"),
            SplitInvoiceScreen.subtotalIs("6.0"),
            SplitInvoiceScreen.clickOrderline("Coca-Cola"),
            SplitInvoiceScreen.orderlineHas("Coca-Cola", "1", "1"),
            SplitInvoiceScreen.subtotalIs("8.0"),

            // click pay to split, go back to check the lines
            SplitInvoiceScreen.clickPay(),
            PaymentScreen.clickBack(),
            ProductScreen.clickOrderline("Water", "3.0"),
            ProductScreen.clickOrderline("Coca-Cola", "1.0"),

            // go back to the original order and see if the order is changed
            Chrome.clickMenuButton(),
            Chrome.clickTicketButton(),
            TicketScreen.selectOrder("-0001"),
            TicketScreen.loadSelectedOrder(),
            ProductScreen.isShown(),
            ProductScreen.clickOrderline("Water", "2.0"),
            ProductScreen.clickOrderline("Minute Maid", "3.0"),
        ].flat(),
});

registry.category("web_tour.tours").add("SplitInvoiceScreenTour2", {
    test: true,
    url: "/pos/ui",
    steps: () =>
        [
            ProductScreen.confirmOpeningPopup(),
            FloorScreen.clickSection("2"),
            ProductScreen.addOrderline("Water", "1", "2.0"),
            ProductScreen.addOrderline("Minute Maid", "1", "2.0"),
            ProductScreen.addOrderline("Coca-Cola", "1", "2.0"),
            FloorScreen.backToFloor(),
            FloorScreen.clickSection("2"),
            ProductScreen.clickSplitInvoiceButton(),

            SplitInvoiceScreen.clickOrderline("Water"),
            SplitInvoiceScreen.orderlineHas("Water", "1", "1"),
            SplitInvoiceScreen.clickOrderline("Coca-Cola"),
            SplitInvoiceScreen.orderlineHas("Coca-Cola", "1", "1"),
            SplitInvoiceScreen.clickPay(),
            PaymentScreen.clickBack(),
            Chrome.clickMenuButton(),
            Chrome.clickTicketButton(),
            TicketScreen.selectOrder("-0002"),
            TicketScreen.loadSelectedOrder(),
            ProductScreen.clickOrderline("Water", "1.0"),
            ProductScreen.clickOrderline("Coca-Cola", "1.0"),
            ProductScreen.totalAmountIs("4.00"),
            Chrome.clickMenuButton(),
            Chrome.clickTicketButton(),
            TicketScreen.selectOrder("-0001"),
            TicketScreen.loadSelectedOrder(),
            Order.hasLine({ productName: "Minute Maid", quantity: "1.0", withClass: ".selected" }),
            ProductScreen.totalAmountIs("2.00"),
        ].flat(),
});

registry.category("web_tour.tours").add("SplitInvoiceScreenTour3", {
    test: true,
    url: "/pos/ui",
    steps: () =>
        [
            ProductScreen.confirmOpeningPopup(),
            FloorScreen.clickSection("2"),
            ProductScreen.addOrderline("Water", "2", "2", "4.00"),
            ProductScreen.clickSplitInvoiceButton(),

            // Check if the screen contains all the orderlines
            SplitInvoiceScreen.orderlineHas("Water", "2", "0"),

            // split 1 water
            SplitInvoiceScreen.clickOrderline("Water"),
            SplitInvoiceScreen.orderlineHas("Water", "2", "1"),
            SplitInvoiceScreen.subtotalIs("2.0"),

            // click pay to split, and pay
            SplitInvoiceScreen.clickPay(),
            PaymentScreen.clickPaymentMethod("Bank"),
            PaymentScreen.clickValidate(),
            // Check if the receiptscreen suggests us to continue the order
            ReceiptScreen.clickContinueOrder(),

            // Check if there is still water in the order
            ProductScreen.isShown(),
            ProductScreen.selectedOrderlineHas("Water", "1.0"),
            ProductScreen.clickPayButton(true),
            PaymentScreen.clickPaymentMethod("Bank"),
            PaymentScreen.clickValidate(),
            // Check if there is no more order to continue
            ReceiptScreen.clickNextOrder(),
        ].flat(),
});

registry.category("web_tour.tours").add("SplitInvoiceScreenTour4PosCombo", {
    test: true,
    url: "/pos/ui",
    steps: () => [
        ...ProductScreen.confirmOpeningPopup(),
        ...FloorScreen.clickSection("2"),

        ...ProductScreen.clickHomeCategory(),
        ...ProductScreen.clickDisplayedProduct("Office Combo"),
        combo.select("Combo Product 3"),
        combo.select("Combo Product 5"),
        combo.select("Combo Product 8"),
        combo.confirm(),

        ...ProductScreen.clickDisplayedProduct("Office Combo"),
        combo.select("Combo Product 2"),
        combo.select("Combo Product 4"),
        combo.select("Combo Product 7"),
        combo.confirm(),

        ...ProductScreen.addOrderline("Water", "1"),
        ...ProductScreen.addOrderline("Minute Maid", "1"),

        // The water and the first combo will go in the new splitted order
        // we will then check if the rest of the items from this combo
        // are automatically sent to the new order.
        ...ProductScreen.clickSplitInvoiceButton(),
        ...SplitInvoiceScreen.clickOrderline("Water"),
        ...SplitInvoiceScreen.clickOrderline("Combo Product 3"),
        // we check that all the lines in the combo are splitted together
        ...SplitInvoiceScreen.orderlineHas("Water", "1", "1"),
        ...SplitInvoiceScreen.orderlineHas("Office Combo", "1", "1"),
        ...SplitInvoiceScreen.orderlineHas("Combo Product 3", "1", "1"),
        ...SplitInvoiceScreen.orderlineHas("Combo Product 5", "1", "1"),
        ...SplitInvoiceScreen.orderlineHas("Combo Product 8", "1", "1"),
        ...SplitInvoiceScreen.orderlineHas("Office Combo", "1", "1"),
        ...SplitInvoiceScreen.orderlineHas("Combo Product 2", "1", "0"),
        ...SplitInvoiceScreen.orderlineHas("Combo Product 4", "1", "0"),
        ...SplitInvoiceScreen.orderlineHas("Combo Product 7", "1", "0"),

        ...SplitInvoiceScreen.subtotalIs("54.13"),
        ...SplitInvoiceScreen.clickPay(),
        ...PaymentScreen.clickPaymentMethod("Bank"),
        ...PaymentScreen.clickValidate(),
        ...ReceiptScreen.clickContinueOrder(),
        // Check if there is still water in the order
        ...ProductScreen.isShown(),
        // now we check that all the lines that remained in the order are correct
        ...ProductScreen.selectedOrderlineHas("Minute Maid", "1.0"),
        ...ProductScreen.clickOrderline("Office Combo"),
        ...ProductScreen.clickOrderline("Combo Product 2"),
        ...ProductScreen.selectedOrderlineHas("Combo Product 2", "1.0", "6.67", "Office Combo"),
        ...ProductScreen.clickOrderline("Combo Product 4"),
        ...ProductScreen.selectedOrderlineHas("Combo Product 4", "1.0", "14.66", "Office Combo"),
        ...ProductScreen.clickOrderline("Combo Product 7"),
        ...ProductScreen.selectedOrderlineHas("Combo Product 7", "1.0", "22.00", "Office Combo"),
        ...ProductScreen.totalAmountIs("45.86"),
    ],
});
