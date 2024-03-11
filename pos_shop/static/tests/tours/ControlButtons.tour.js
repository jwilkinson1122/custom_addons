/** @odoo-module */

import * as TextAreaPopup from "@point_of_sale/../tests/tours/helpers/TextAreaPopupTourMethods";
import * as NumberPopup from "@point_of_sale/../tests/tours/helpers/NumberPopupTourMethods";
import * as FloorScreen from "@pos_shop/../tests/tours/helpers/FloorScreenTourMethods";
import * as ProductScreenPos from "@point_of_sale/../tests/tours/helpers/ProductScreenTourMethods";
import * as ProductScreenResto from "@pos_shop/../tests/tours/helpers/ProductScreenTourMethods";
const ProductScreen = { ...ProductScreenPos, ...ProductScreenResto };
import * as SplitInvoiceScreen from "@pos_shop/../tests/tours/helpers/SplitInvoiceScreenTourMethods";
import * as InvoiceScreen from "@pos_shop/../tests/tours/helpers/InvoiceScreenTourMethods";
import * as Order from "@point_of_sale/../tests/tours/helpers/generic_components/OrderWidgetMethods";
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("ControlButtonsTour", {
    test: true,
    url: "/pos/ui",
    steps: () =>
        [
            // Test TransferOrderButton
            FloorScreen.clickSection("2"),
            ProductScreen.addOrderline("Water", "5", "2", "10.0"),
            ProductScreen.clickTransferButton(),
            FloorScreen.clickSection("4"),
            FloorScreen.backToFloor(),
            FloorScreen.clickSection("2"),
            ProductScreen.orderIsEmpty(),
            FloorScreen.backToFloor(),
            FloorScreen.clickSection("4"),

            // Test SplitInvoiceButton
            ProductScreen.clickSplitInvoiceButton(),
            SplitInvoiceScreen.clickBack(),

            // Test OrderlineNoteButton
            ProductScreen.clickNoteButton(),
            TextAreaPopup.isShown(),
            TextAreaPopup.inputText("test note"),
            TextAreaPopup.clickConfirm(),
            Order.hasLine({
                productName: "Water",
                quantity: "5",
                price: "10.0",
                internalNote: "test note",
                withClass: ".selected",
            }),
            ProductScreen.addOrderline("Water", "8", "1", "8.0"),

            // Test PrintInvoiceButton
            ProductScreen.clickPrintInvoiceButton(),
            InvoiceScreen.isShown(),
            InvoiceScreen.clickOk(),

            // Test GuestButton
            ProductScreen.clickGuestButton(),
            NumberPopup.enterValue("15"),
            NumberPopup.inputShownIs("15"),
            NumberPopup.clickConfirm(),
            ProductScreen.guestNumberIs("15"),

            ProductScreen.clickGuestButton(),
            NumberPopup.enterValue("5"),
            NumberPopup.inputShownIs("5"),
            NumberPopup.clickConfirm(),
            ProductScreen.guestNumberIs("5"),
        ].flat(),
});
