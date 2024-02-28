/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PrescriptionsActivityModel } from "@prescriptions/views/activity/prescriptions_activity_model";

import { XLSX_MIME_TYPE } from "@prescriptions_spreadsheet/helpers";

patch(PrescriptionsActivityModel.Record.prototype, {
    /**
     * @override
     */
    isViewable() {
        return (
            this.data.handler === "spreadsheet" || this.data.mimetype === XLSX_MIME_TYPE || super.isViewable(...arguments)
        );
    },
});
