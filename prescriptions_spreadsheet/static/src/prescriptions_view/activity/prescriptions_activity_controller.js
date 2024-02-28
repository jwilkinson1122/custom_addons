/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PrescriptionsActivityController } from "@prescriptions/views/activity/prescriptions_activity_controller";
import { PrescriptionsSpreadsheetControllerMixin } from "../prescriptions_spreadsheet_controller_mixin";

patch(PrescriptionsActivityController.prototype, PrescriptionsSpreadsheetControllerMixin());

patch(PrescriptionsActivityController.prototype, {
    /**
     * Prevents spreadsheets from being in the viewable attachments list
     * when previewing a file in the activity view.
     *
     * @override
     */
    isRecordPreviewable(record) {
        return super.isRecordPreviewable(...arguments) && record.data.handler !== "spreadsheet";
    },
});
