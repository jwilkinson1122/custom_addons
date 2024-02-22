/** @odoo-module **/
import { registry } from "@web/core/registry";
import { kanbanView } from '@web/views/kanban/kanban_view';
import { KanbanRenderer } from '@web/views/kanban/kanban_renderer';
import { PrescriptionDashBoard } from '@pod_mini_dashboard/js/prescription_dashboard';

/**
 * Prescription Dashboard Kanban Renderer class, extending the base KanbanRenderer.
 * @extends KanbanRenderer
 */
export class PrescriptionDashBoardKanbanRenderer extends KanbanRenderer {};

// Template for the PrescriptionDashBoardKanbanRenderer component
PrescriptionDashBoardKanbanRenderer.template = 'pod_mini_dashboard.PrescriptionKanbanView';

// Components used by PrescriptionDashBoardKanbanRenderer
PrescriptionDashBoardKanbanRenderer.components = Object.assign({}, KanbanRenderer.components, { PrescriptionDashBoard });

/**
 * Prescription Dashboard Kanban View configuration.
 * @type {Object}
 */
export const PrescriptionDashBoardKanbanView = {
    ...kanbanView,
    // Use the custom PrescriptionDashBoardKanbanRenderer as the renderer for the kanban view
    Renderer: PrescriptionDashBoardKanbanRenderer,
};

// Register the Prescription Dashboard Kanban View in the "views" category of the registry
registry.category("views").add("prescription_dashboard_kanban", PrescriptionDashBoardKanbanView);
