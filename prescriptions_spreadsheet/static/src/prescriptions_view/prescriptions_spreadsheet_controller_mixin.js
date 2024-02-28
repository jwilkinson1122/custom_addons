/** @odoo-module **/

import { TemplateDialog } from "@prescriptions_spreadsheet/spreadsheet_template/spreadsheet_template_dialog";
import { useService } from "@web/core/utils/hooks";
import { loadBundle } from "@web/core/assets";

import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { SpreadsheetCloneXlsxDialog } from "@prescriptions_spreadsheet/spreadsheet_clone_xlsx_dialog/spreadsheet_clone_xlsx_dialog";
import { _t } from "@web/core/l10n/translation";

import { XLSX_MIME_TYPE } from "@prescriptions_spreadsheet/helpers";

export const PrescriptionsSpreadsheetControllerMixin = () => ({
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        this.action = useService("action");
        this.dialogService = useService("dialog");
        // Hack-ish way to do this but the function is added by a hook which we can't really override.
        this.baseOnOpenPrescriptionsPreview = this.onOpenPrescriptionsPreview.bind(this);
        this.onOpenPrescriptionsPreview = this._onOpenPrescriptionsPreview.bind(this);
    },

    /**
     * @override
     */
    prescriptionsViewHelpers() {
        return {
            ...super.prescriptionsViewHelpers(),
            sharePopupAction: this.sharePopupAction.bind(this),
        };
    },

    async sharePopupAction(prescriptionShareVals) {
        const selection = this.env.model.root.selection;
        const prescriptions = selection.length ? selection : this.env.model.root.records;
        if (
            this.env.model.useSampleModel ||
            prescriptions.every((doc) => doc.data.handler !== "spreadsheet")
        ) {
            return prescriptionShareVals;
        }
        const spreadsheetShares = [];
        for (const doc of prescriptions) {
            if (doc.data.handler === "spreadsheet") {
                const resId = doc.resId;
                await loadBundle("spreadsheet.o_spreadsheet");
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
            ...prescriptionShareVals,
            spreadsheet_shares: spreadsheetShares,
        };
    },

    /**
     * @override
     */
    async _onOpenPrescriptionsPreview({ prescriptions }) {
        if (
            prescriptions.length !== 1 ||
            (prescriptions[0].data.handler !== "spreadsheet" &&
                prescriptions[0].data.mimetype !== XLSX_MIME_TYPE)
        ) {
            return this.baseOnOpenPrescriptionsPreview(...arguments);
        }
        if (prescriptions[0].data.handler === "spreadsheet") {
            this.action.doAction({
                type: "ir.actions.client",
                tag: "action_open_spreadsheet",
                params: {
                    spreadsheet_id: prescriptions[0].resId,
                },
            });
        } else if (prescriptions[0].data.mimetype === XLSX_MIME_TYPE) {
            if (!prescriptions[0].data.active) {
                this.dialogService.add(ConfirmationDialog, {
                    title: _t("Restore file?"),
                    body: _t(
                        "Spreadsheet files cannot be handled from the Trash. Would you like to restore this prescription?"
                    ),
                    cancel: () => {},
                    confirm: async () => {
                        await this.orm.call("prescriptions.prescription", "action_unarchive", [
                            prescriptions[0].resId,
                        ]);
                        this.env.searchModel.toggleCategoryValue(1, prescriptions[0].data.folder_id[0]);
                    },
                    confirmLabel: _t("Restore"),
                });
            } else {
                this.dialogService.add(SpreadsheetCloneXlsxDialog, {
                    title: _t("Format issue"),
                    cancel: () => {},
                    cancelLabel: _t("Discard"),
                    prescriptionId: prescriptions[0].resId,
                    confirmLabel: _t("Open with Odoo Spreadsheet"),
                });
            }
        }
    },

    async onClickCreateSpreadsheet(ev) {
        this.dialogService.add(TemplateDialog, {
            folderId: this.env.searchModel.getSelectedFolderId() || undefined,
            context: this.props.context,
            folders: this.env.searchModel.getFolders().slice(1),
        });
    },
});
