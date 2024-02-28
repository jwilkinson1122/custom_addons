/** @odoo-module **/

import { registry } from "@web/core/registry";

import { activityView } from "@mail/views/web/activity/activity_view";
import { PrescriptionsActivityController } from "./prescriptions_activity_controller";
import { PrescriptionsActivityModel } from "./prescriptions_activity_model";
import { PrescriptionsActivityRenderer } from "./prescriptions_activity_renderer";
import { PrescriptionsSearchModel } from "../search/prescriptions_search_model";

export const PrescriptionsActivityView = {
    ...activityView,
    Controller: PrescriptionsActivityController,
    Model: PrescriptionsActivityModel,
    Renderer: PrescriptionsActivityRenderer,
    SearchModel: PrescriptionsSearchModel,
};
registry.category("views").add("prescriptions_activity", PrescriptionsActivityView);
