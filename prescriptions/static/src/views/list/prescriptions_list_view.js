/** @odoo-module **/

import { registry } from "@web/core/registry";

import { listView } from "@web/views/list/list_view";
import { PrescriptionsListController } from "./prescriptions_list_controller";
import { PrescriptionsListModel } from "./prescriptions_list_model";
import { PrescriptionsListRenderer } from "./prescriptions_list_renderer";
import { PrescriptionsSearchModel } from "../search/prescriptions_search_model";
import { PrescriptionsSearchPanel } from "../search/prescriptions_search_panel";


export const PrescriptionsListView = Object.assign({}, listView, {
    SearchModel: PrescriptionsSearchModel,
    SearchPanel: PrescriptionsSearchPanel,
    Controller: PrescriptionsListController,
    Model: PrescriptionsListModel,
    Renderer: PrescriptionsListRenderer,
    searchMenuTypes: ["filter", "groupBy", "favorite"],
});

registry.category("views").add("prescriptions_list", PrescriptionsListView);
