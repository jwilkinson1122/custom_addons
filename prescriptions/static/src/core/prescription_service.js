/* @odoo-module */

import { Prescription } from "./prescription_model";
import { registry } from "@web/core/registry";

export class PrescriptionService {
    prescriptionList;

    constructor(env, services) {
        this.env = env;
        this.rpc = services.rpc;
        /** @type {import("@mail/core/common/store_service").Store} */
        this.store = services["mail.store"];
        /** @type {import("@mail/core/common/attachment_service").AttachmentService} */
        this.attachmentService = services["mail.attachment"];
    }

    /**
     * @param {Object} data
     * @returns {Prescription}
     */
    insert(data) {
        let prescription = this.store.Prescription.records[data.id];
        if (!prescription) {
            prescription = new Prescription();
            if ("id" in data) {
                prescription.id = data.id;
            }
            if ("attachment" in data) {
                prescription.attachment = this.store.Attachment.insert(data.attachment);
            }
            if ("name" in data) {
                prescription.name = data.name;
            }
            if ("mimetype" in data) {
                prescription.mimetype = data.mimetype;
            }
            if ("url" in data) {
                prescription.url = data.url;
            }
            if ("displayName" in data) {
                prescription.displayName = data.displayName;
            }
            if ("record" in data) {
                prescription.record = data.record;
            }
            prescription._store = this.store;
            this.store.Prescription.records[data.id] = prescription;
            // Get reactive version.
            prescription = this.store.Prescription.records[data.id];
        }
        // return reactive version
        return prescription;
    }
}

export const prescriptionService = {
    dependencies: ["rpc", "mail.store", "mail.attachment"],
    start(env, services) {
        return new PrescriptionService(env, services);
    },
};

registry.category("services").add("prescription.prescription", prescriptionService);
