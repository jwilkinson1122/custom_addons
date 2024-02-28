/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PrescriptionsKanbanRecord } from "@prescriptions/views/kanban/prescriptions_kanban_model";

import { XLSX_MIME_TYPE } from "@prescriptions_spreadsheet/helpers";

patch(PrescriptionsKanbanRecord.prototype, {
    /**
     * @override
     */
    isViewable() {
        return (
            this.data.handler === "spreadsheet" ||
            this.data.mimetype === XLSX_MIME_TYPE ||
            super.isViewable(...arguments)
        );
    },
});
