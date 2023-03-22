/** @odoo-module **/

import ProductKanbanController from "@podiatry_management/js/product_kanbancontroller";
import ProductKanbanModel from "@podiatry_management/js/product_kanbanmodel";
import ProductKanbanRenderer from "@podiatry_management/js/product_kanbanrender";
import KanbanView from "web.KanbanView";
import viewRegistry from "web.view_registry";
import { _lt } from "web.core";


const ProductKanbanView = KanbanView.extend({
    config: _.extend({}, KanbanView.prototype.config, {
        Controller: ProductKanbanController,
        Model: ProductKanbanModel,
        Renderer: ProductKanbanRenderer,
    }),
    display_name: _lt('Product Management'),
    groupable: false,
});


viewRegistry.add("product_kanban", ProductKanbanView);

export default ProductKanbanView;
