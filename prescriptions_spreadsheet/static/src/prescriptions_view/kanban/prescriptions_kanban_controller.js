/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PrescriptionsKanbanController } from "@prescriptions/views/kanban/prescriptions_kanban_controller";
import { PrescriptionsSpreadsheetControllerMixin } from "../prescriptions_spreadsheet_controller_mixin";

patch(PrescriptionsKanbanController.prototype, PrescriptionsSpreadsheetControllerMixin());
