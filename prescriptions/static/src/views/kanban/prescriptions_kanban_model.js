/** @odoo-module **/

import { RelationalModel } from "@web/model/relational_model/relational_model";
import {
    PrescriptionsModelMixin,
    PrescriptionsRecordMixin,
} from "../prescriptions_model_mixin";

export class PrescriptionsKanbanModel extends PrescriptionsModelMixin(RelationalModel) {}

export class PrescriptionsKanbanRecord extends PrescriptionsRecordMixin(RelationalModel.Record) {
    async onClickPreview(ev) {
        if (this.data.type === "empty") {
            // In case the file is actually empty we open the input to replace the file
            ev.stopPropagation();
            ev.target.querySelector(".o_kanban_replace_prescription").click();
        } else if (this.isViewable()) {
            ev.stopPropagation();
            ev.preventDefault();
            const folder = this.model.env.searchModel
                .getFolders()
                .filter((folder) => folder.id === this.data.folder_id[0]);
            const hasPdfSplit =
                (!this.data.lock_uid || this.data.lock_uid[0] === this.model.user.userId) &&
                folder.has_write_access;
            const selection = this.model.root.selection;
            const prescriptions = selection.length > 1 && selection.find(rec => rec === this) && selection.filter(rec => rec.isViewable()) || [this];
            await this.model.env.prescriptionsView.bus.trigger("prescriptions-open-preview", {
                prescriptions,
                mainPrescription: this,
                isPdfSplit: false,
                rules: this.data.available_rule_ids.records,
                hasPdfSplit,
            });
        }
    }

    async onReplacePrescription(ev) {
        if (!ev.target.files.length) {
            return;
        }
        await this.model.env.prescriptionsView.bus.trigger("prescriptions-upload-files", {
            files: ev.target.files,
            folderId: this.data.folder_id && this.data.folder_id[0],
            recordId: this.resId,
            tagIds: this.model.env.searchModel.getSelectedTagIds(),
        });
        ev.target.value = "";
    }
}
PrescriptionsKanbanModel.Record = PrescriptionsKanbanRecord;

