/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PrescriptionsListModel } from "@prescriptions/views/list/prescriptions_list_model";

import { XLSX_MIME_TYPE } from "@prescriptions_spreadsheet/helpers";

patch(PrescriptionsListModel.Record.prototype, {
    /**
     * @override
     */
    isViewable() {
        return (
            this.data.handler === "spreadsheet" || this.data.mimetype === XLSX_MIME_TYPE || super.isViewable(...arguments)
        );
    },
});
