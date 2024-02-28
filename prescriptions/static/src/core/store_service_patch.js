/** @odoo-module */

import { Store } from "@mail/core/common/store_service";

import { patch } from "@web/core/utils/patch";

let self;
patch(Store.prototype, {
    hasPrescriptionsUserGroup: false,
    Prescription: {
        /** @type {Object.<number, import("@prescriptions/core/prescription_model").Prescription>} */
        records: {},
        /**
         * @param {Object} data
         * @returns {import("@prescriptions/core/prescription_model").Prescription}
         */
        insert: (data) => self.env.services["prescription.prescription"].insert(data),
    },
    setup() {
        super.setup();
        self = this;
    },
});
