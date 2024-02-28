/** @odoo-module **/

import { registry } from "@web/core/registry";
import { stepUtils, TourError } from "@web_tour/tour_service/tour_utils";

registry.category("web_tour.tours").add("spreadsheet_save_multipage", {
    test: true,
    steps: () => [
        stepUtils.showAppsMenuItem(),
        {
            trigger: '.o_app[data-menu-xmlid="prescriptions.menu_root"]',
            content: "Open prescription app",
        },
        {
            trigger: ".o_cp_buttons:contains('Upload') .dropdown-toggle.dropdown-toggle-split",
            content: "Open dropdown",
        },
        {
            trigger: ".o_prescriptions_kanban_spreadsheet",
            content: "Open template dialog",
        },
        {
            trigger: ".o-spreadsheet-create",
            content: "Create new spreadsheet",
        },
        {
            trigger: ".o-add-sheet",
            content: "Add a sheet",
        },
        {
            trigger: ".o-sheet-list .o-ripple-container:nth-child(2)",
            content: "Check that there are now two sheets",
            isCheck: true,
        },
        {
            trigger: '[data-menu-xmlid="prescriptions.dashboard"]',
            content: "Go back to Prescription App",
        },
        {
            trigger: ".o_kanban_renderer .o_kanban_record:first .o_kanban_stack ",
            content: "Check is rendered as multipage",
            isCheck: true,
        },
        {
            trigger: ".o_prescription_spreadsheet:first",
            content: "Reopen the sheet",
        },
        {
            trigger: ".o-sheet .o-sheet-icon",
            content: "Open sheet dropdown",
        },
        {
            trigger: '.o-popover .o-menu-item[title="Delete"]',
            content: "Delete sheet",
        },
        {
            trigger: ".modal-dialog footer button.btn-primary",
            content: "Confirm delete sheet",
        },
        {
            trigger: '[data-menu-xmlid="prescriptions.dashboard"]',
            content: "Go back to Prescription App",
        },
        {
            trigger: ".o_kanban_renderer .o_kanban_record:first",
            content: "Check is rendered as single page",
            run: () => {
                const card = prescription.querySelectorAll(
                    ".o_kanban_renderer .o_kanban_record:first-child > div.o_kanban_stack"
                );
                if (card.length > 1) {
                    throw new TourError("The card should not be rendered as multipage.");
                }
            },
        },
    ],
});
