/** @odoo-module **/

import { registry } from "@web/core/registry";

import { kanbanView } from "@web/views/kanban/kanban_view";
import { PrescriptionsKanbanController } from "./prescriptions_kanban_controller";
import { PrescriptionsKanbanModel } from "./prescriptions_kanban_model";
import { PrescriptionsKanbanRenderer } from "./prescriptions_kanban_renderer";
import { PrescriptionsSearchModel } from "../search/prescriptions_search_model";
import { PrescriptionsSearchPanel } from "../search/prescriptions_search_panel";


export const PrescriptionsKanbanView = Object.assign({}, kanbanView, {
    SearchModel: PrescriptionsSearchModel,
    SearchPanel: PrescriptionsSearchPanel,
    Controller: PrescriptionsKanbanController,
    Model: PrescriptionsKanbanModel,
    Renderer: PrescriptionsKanbanRenderer,
    searchMenuTypes: ["filter", "favorite"],
});

registry.category("views").add("prescriptions_kanban", PrescriptionsKanbanView);
