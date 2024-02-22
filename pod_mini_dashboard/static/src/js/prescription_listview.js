/** @odoo-module **/
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { PrescriptionDashBoard } from '@pod_mini_dashboard/js/prescription_dashboard';

/**
 * Prescription Dashboard Renderer class for list view, extending the base ListRenderer.
 * @extends ListRenderer
 */
export class PrescriptionDashBoardRenderer extends ListRenderer {};

// Template for the PrescriptionDashBoardRenderer component
PrescriptionDashBoardRenderer.template = 'pod_mini_dashboard.PrescriptionListView';

// Components used by PrescriptionDashBoardRenderer
PrescriptionDashBoardRenderer.components = Object.assign({}, ListRenderer.components, { PrescriptionDashBoard });

/**
 * Prescription Dashboard List View configuration.
 * @type {Object}
 */
export const PrescriptionDashBoardListView = {
    ...listView,
    // Use the custom PrescriptionDashBoardRenderer as the renderer for the list view
    Renderer: PrescriptionDashBoardRenderer,
};

// Register the Prescription Dashboard List View in the "views" category of the registry
registry.category("views").add("prescription_dashboard_list", PrescriptionDashBoardListView);
