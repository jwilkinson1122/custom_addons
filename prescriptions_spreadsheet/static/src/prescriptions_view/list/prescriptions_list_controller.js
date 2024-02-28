/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PrescriptionsListController } from "@prescriptions/views/list/prescriptions_list_controller";
import { PrescriptionsSpreadsheetControllerMixin } from "../prescriptions_spreadsheet_controller_mixin";

patch(PrescriptionsListController.prototype, PrescriptionsSpreadsheetControllerMixin());
