/* @odoo-module */

import { Attachment } from "@mail/core/common/attachment_model";
import { patch } from "@web/core/utils/patch";
import { assignDefined } from "@mail/utils/common/misc";

patch(Attachment.prototype, {
    prescriptionId: null,

    update(data) {
        super.update(data);
        assignDefined(this, data, ["prescriptionId"]);
    },

    get urlRoute() {
        if (this.prescriptionId) {
            return this.isImage
                ? `/web/image/${this.prescriptionId}`
                : `/web/content/${this.prescriptionId}`;
        }
        return super.urlRoute;
    },

    get urlQueryParams() {
        const res = super.urlQueryParams;
        if (this.prescriptionId) {
            res["model"] = "prescriptions.prescription";
            return res;
        }
        return res;
    },
});
