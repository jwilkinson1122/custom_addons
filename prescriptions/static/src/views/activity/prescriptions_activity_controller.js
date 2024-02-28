/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ActivityController } from "@mail/views/web/activity/activity_controller";

import { preSuperSetup, usePrescriptionView } from "@prescriptions/views/hooks";
import { useState } from "@odoo/owl";

export class PrescriptionsActivityController extends ActivityController {
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

    get rendererProps() {
        const props = super.rendererProps;
        props.inspectedPrescriptions = this.prescriptionStates.inspectedPrescriptions;
        props.previewStore = this.prescriptionStates.previewStore;
        return props;
    }

    /**
     * Override this to add view options.
     */
    prescriptionsViewHelpers() {
        return {
            getSelectedPrescriptionsElements: () => [],
            isRecordPreviewable: this.isRecordPreviewable.bind(this),
            setInspectedPrescriptions: (inspectedPrescriptions) => {
                this.prescriptionStates.inspectedPrescriptions = inspectedPrescriptions;
            },
            setPreviewStore: (previewStore) => {
                this.prescriptionStates.previewStore = previewStore;
            },
        };
    }

    /**
     * Select record for inspector.
     *
     * @override
     */
    async openRecord(record, mode) {
        for (const record of this.model.root.selection) {
            record.selected = false;
        }
        record.selected = true;
        this.model.notify();
    }

    /**
     * @returns {Boolean} whether the record can be previewed in the attachment viewer.
     */
    isRecordPreviewable(record) {
        return this.model.activityData.activity_res_ids.includes(record.resId);
    }

    /**
     * @override
     * @param {number} [templateID]
     * @param {number} [activityTypeID]
     */
    sendMailTemplate(templateID, activityTypeID) {
        super.sendMailTemplate(templateID, activityTypeID);
        this.env.services.notification.add(_t("Reminder emails have been sent."), {
            type: "success",
        });
    }
}
PrescriptionsActivityController.template = "prescriptions.PrescriptionsActivityController";
