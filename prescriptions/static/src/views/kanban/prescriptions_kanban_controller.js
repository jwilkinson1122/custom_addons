/** @odoo-module **/

import { KanbanController } from "@web/views/kanban/kanban_controller";

import { preSuperSetup, usePrescriptionView } from "@prescriptions/views/hooks";
import { useState } from "@odoo/owl";

export class PrescriptionsKanbanController extends KanbanController {
    setup() {
        preSuperSetup();
        super.setup(...arguments);
        const properties = usePrescriptionView(this.prescriptionsViewHelpers());
        Object.assign(this, properties);

        this.prescriptionStates = useState({
            inspectedPrescriptions: [],
            previewStore: {},
        });
    }

    get modelParams() {
        const modelParams = super.modelParams;
        modelParams.multiEdit = true;
        return modelParams;
    }

    /**
     * Override this to add view options.
     */
    prescriptionsViewHelpers() {
        return {
            getSelectedPrescriptionsElements: () =>
                this.root.el.querySelectorAll(".o_kanban_record.o_record_selected"),
            setInspectedPrescriptions: (inspectedPrescriptions) => {
                this.prescriptionStates.inspectedPrescriptions = inspectedPrescriptions;
            },
            setPreviewStore: (previewStore) => {
                this.prescriptionStates.previewStore = previewStore;
            },
        };
    }
}
PrescriptionsKanbanController.template = "prescriptions.PrescriptionsKanbanView";
