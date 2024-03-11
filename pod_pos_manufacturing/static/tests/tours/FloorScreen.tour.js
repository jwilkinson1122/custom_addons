/** @odoo-module */

import * as Chrome from "@point_of_sale/../tests/tours/helpers/ChromeTourMethods";
import * as FloorScreen from "@pod_pos_manufacturing/../tests/tours/helpers/FloorScreenTourMethods";
import * as TextInputPopup from "@point_of_sale/../tests/tours/helpers/TextInputPopupTourMethods";
import * as NumberPopup from "@point_of_sale/../tests/tours/helpers/NumberPopupTourMethods";
import * as ProductScreenPos from "@point_of_sale/../tests/tours/helpers/ProductScreenTourMethods";
import * as ProductScreenResto from "@pod_pos_manufacturing/../tests/tours/helpers/ProductScreenTourMethods";
const ProductScreen = { ...ProductScreenPos, ...ProductScreenResto };
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("FloorScreenTour", {
    test: true,
    url: "/pos/ui",
    steps: () =>
        [
            // check floors if they contain their corresponding sections
            FloorScreen.selectedFloorIs("Main Floor"),
            FloorScreen.hasSection("2"),
            FloorScreen.hasSection("4"),
            FloorScreen.hasSection("5"),
            FloorScreen.clickFloor("Second Floor"),
            FloorScreen.hasSection("3"),
            FloorScreen.hasSection("1"),

            // clicking section in active mode does not open product screen
            // instead, section is selected
            FloorScreen.clickEdit(),
            FloorScreen.clickSection("3"),
            FloorScreen.selectedSectionIs("3"),
            FloorScreen.clickSection("1"),
            FloorScreen.selectedSectionIs("1"),

            // test add section
            FloorScreen.clickFloor("Main Floor"),
            FloorScreen.clickAddSection(),
            FloorScreen.selectedSectionIs("1"),
            FloorScreen.clickRename(),
            TextInputPopup.isShown(),
            TextInputPopup.inputText("100"),
            TextInputPopup.clickConfirm(),
            FloorScreen.clickSection("100"),
            FloorScreen.selectedSectionIs("100"),

            // test duplicate section
            FloorScreen.clickDuplicate(),
            // the name is the first number available on the floor
            FloorScreen.selectedSectionIs("1"),
            FloorScreen.clickRename(),
            TextInputPopup.isShown(),
            TextInputPopup.inputText("1111"),
            TextInputPopup.clickConfirm(),
            FloorScreen.clickSection("1111"),
            FloorScreen.selectedSectionIs("1111"),

            // switch floor, switch back and check if
            // the new sections are still there
            FloorScreen.clickFloor("Second Floor"),
            FloorScreen.hasSection("3"),
            FloorScreen.hasSection("1"),

            //test duplicate multiple sections
            FloorScreen.clickSection("1"),
            FloorScreen.selectedSectionIs("1"),
            FloorScreen.ctrlClickSection("3"),
            FloorScreen.selectedSectionIs("3"),
            FloorScreen.clickDuplicate(),
            FloorScreen.selectedSectionIs("2"),
            FloorScreen.selectedSectionIs("4"),

            //test delete multiple sections
            FloorScreen.clickTrash(),
            Chrome.confirmPopup(),

            FloorScreen.clickFloor("Main Floor"),
            FloorScreen.hasSection("2"),
            FloorScreen.hasSection("4"),
            FloorScreen.hasSection("5"),
            FloorScreen.hasSection("100"),
            FloorScreen.hasSection("1111"),

            // test delete section
            FloorScreen.clickSection("2"),
            FloorScreen.selectedSectionIs("2"),
            FloorScreen.clickTrash(),
            Chrome.confirmPopup(),

            // change number of seats
            FloorScreen.clickSection("4"),
            FloorScreen.selectedSectionIs("4"),
            FloorScreen.clickSeats(),
            NumberPopup.pressNumpad("⌫ 9"),
            NumberPopup.fillPopupValue("9"),
            NumberPopup.inputShownIs("9"),
            NumberPopup.clickConfirm(),
            FloorScreen.sectionSeatIs("4", "9"),

            // change number of seat when the input is already selected
            FloorScreen.clickSection("4"),
            FloorScreen.selectedSectionIs("4"),
            FloorScreen.clickSeats(),
            NumberPopup.enterValue("15"),
            NumberPopup.inputShownIs("15"),
            NumberPopup.clickConfirm(),
            FloorScreen.sectionSeatIs("4", "15"),

            // change shape
            FloorScreen.clickSection("4"),
            FloorScreen.changeShapeTo("round"),

            // Opening product screen in main floor should go back to main floor
            FloorScreen.closeEdit(),
            FloorScreen.sectionIsNotSelected("4"),
            FloorScreen.clickSection("4"),
            ProductScreen.isShown(),
            FloorScreen.backToFloor(),

            // Opening product screen in second floor should go back to second floor
            FloorScreen.clickFloor("Second Floor"),
            FloorScreen.hasSection("3"),
            FloorScreen.clickSection("3"),
        ].flat(),
});
