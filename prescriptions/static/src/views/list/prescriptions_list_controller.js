/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { _t } from "@web/core/l10n/translation";
import { preSuperSetup, usePrescriptionView } from "@prescriptions/views/hooks";
import { useState } from "@odoo/owl";

export class PrescriptionsListController extends ListController {
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

    onWillSaveMultiRecords() {}

    onSavedMultiRecords() {}

    /**
     * Override this to add view options.
     */
    prescriptionsViewHelpers() {
        return {
            getSelectedPrescriptionsElements: () =>
                this.root.el.querySelectorAll(
                    ".o_data_row.o_data_row_selected .o_list_record_selector"
                ),
            setInspectedPrescriptions: (inspectedPrescriptions) => {
                this.prescriptionStates.inspectedPrescriptions = inspectedPrescriptions;
            },
            setPreviewStore: (previewStore) => {
                this.prescriptionStates.previewStore = previewStore;
            },
        };
    }

    getStaticActionMenuItems() {
        const isM2MGrouped = this.model.root.isM2MGrouped;
        const active = this.model.root.records[0].isActive;
        return {
            export: {
                isAvailable: () => this.isExportEnable,
                sequence: 10,
                description: _t("Export"),
                callback: () => this.onExportData(),
            },
            delete: {
                isAvailable: () => this.activeActions.delete && !isM2MGrouped,
                sequence: 40,
                description: _t("Delete"),
                callback: active
                    ? () => this.onArchiveSelectedRecords()
                    : () => this.onDeleteSelectedRecords(),
            },
        };
    }

    onDeleteSelectedRecords() {
        const root = this.model.root;
        const callback = async () => {
            await root.deleteRecords(root.records.filter((record) => record.selected));
            await this.model.notify();
        };
        root.records[0].openDeleteConfirmationDialog(root, callback, true);
    }

    onArchiveSelectedRecords() {
        const root = this.model.root;
        const callback = async () => {
            await this.toggleArchiveState(true);
        };
        root.records[0].openDeleteConfirmationDialog(root, callback, false);
    }
}

PrescriptionsListController.template = "prescriptions.PrescriptionsListController";
