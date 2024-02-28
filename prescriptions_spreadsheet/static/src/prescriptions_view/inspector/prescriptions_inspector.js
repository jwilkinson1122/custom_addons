/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { loadBundle } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";
import {
    inspectorFields,
    PrescriptionsInspector,
} from "@prescriptions/views/inspector/prescriptions_inspector";

import { XLSX_MIME_TYPE } from "@prescriptions_spreadsheet/helpers";

inspectorFields.push("handler");

patch(PrescriptionsInspector.prototype, {
    /**
     * @override
     */
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.notification = useService("notification");
    },

    /**
     * @override
     */
    getRecordAdditionalData(record) {
        const result = super.getRecordAdditionalData(...arguments);
        result.isSheet = record.data.handler === "spreadsheet";
        result.isXlsx = record.data.mimetype === XLSX_MIME_TYPE;
        return result;
    },

    /**
     * @override
     */
    getPreviewClasses(record, additionalData) {
        let result = super.getPreviewClasses(...arguments);
        if (additionalData.isSheet) {
            return result.replace("o_prescriptions_preview_mimetype", "o_prescriptions_preview_image");
        }
        if (additionalData.isXlsx) {
            result += " o_prescription_xlsx";
        }
        return result;
    },

    openSpreadsheet(record) {
        this.env.bus.trigger("prescriptions-open-preview", {
            prescriptions: [record],
            isPdfSplit: false,
            rules: [],
            hasPdfSplit: false,
        });
    },

    /**
     * @override
     */
    async onDownload() {
        const selection = this.props.prescriptions || [];
        if (selection.some((record) => record.data.handler === "spreadsheet")) {
            if (selection.length === 1) {
                const record = await this.orm.call(
                    "prescriptions.prescription",
                    "join_spreadsheet_session",
                    [selection[0].resId]
                );
                await this.action.doAction({
                    type: "ir.actions.client",
                    tag: "action_download_spreadsheet",
                    params: {
                        orm: this.orm,
                        name: record.name,
                        data: record.data,
                        stateUpdateMessages: record.revisions,
                    },
                });
            } else {
                this.notification.add(
                    _t(
                        "Spreadsheets mass download not yet supported.\n Download spreadsheets individually instead."
                    ),
                    {
                        sticky: false,
                        type: "danger",
                    }
                );
                const docs = selection.filter(
                    (doc) => doc.data.handler !== "spreadsheet" && doc.data.type !== "empty"
                );
                if (docs.length) {
                    this.download(selection.filter((rec) => rec.data.handler !== "spreadsheet"));
                }
            }
        } else {
            super.onDownload(...arguments);
        }
    },

    /**
     * @override
     */
    async createShareVals() {
        const selection = this.props.prescriptions;
        const vals = await super.createShareVals();
        if (selection.every((doc) => doc.data.handler !== "spreadsheet")) {
            return vals;
        }
        await loadBundle("spreadsheet.o_spreadsheet");
        const spreadsheetShares = [];
        for (const prescription of selection) {
            if (prescription.data.handler === "spreadsheet") {
                const resId = prescription.resId;
                const { fetchSpreadsheetModel, freezeOdooData } = odoo.loader.modules.get("@spreadsheet/helpers/model");
                const model = await fetchSpreadsheetModel(this.env, "prescriptions.prescription", resId);
                const data = await freezeOdooData(model);
                spreadsheetShares.push({
                    spreadsheet_data: JSON.stringify(data),
                    excel_files: model.exportXLSX().files,
                    prescription_id: resId,
                });
            }
        }
        return {
            ...vals,
            spreadsheet_shares: spreadsheetShares,
        };
    },
});
