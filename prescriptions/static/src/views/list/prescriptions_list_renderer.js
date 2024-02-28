/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ListRenderer } from "@web/views/list/list_renderer";

import { useService } from "@web/core/utils/hooks";
import { PrescriptionsInspector } from "../inspector/prescriptions_inspector";
import { FileUploadProgressContainer } from "@web/core/file_upload/file_upload_progress_container";
import { FileUploadProgressDataRow } from "@web/core/file_upload/file_upload_progress_record";
import { PrescriptionsDropZone } from "../helper/prescriptions_drop_zone";
import { PrescriptionsActionHelper } from "../helper/prescriptions_action_helper";
import { PrescriptionsFileViewer } from "../helper/prescriptions_file_viewer";
import { PrescriptionsListRendererCheckBox } from "./prescriptions_list_renderer_checkbox";
import { useCommand } from "@web/core/commands/command_hook";
import { useRef } from "@odoo/owl";

export class PrescriptionsListRenderer extends ListRenderer {
    static props = [...ListRenderer.props, "inspectedPrescriptions", "previewStore"];
    static template = "prescriptions.PrescriptionsListRenderer";
    static recordRowTemplate = "prescriptions.PrescriptionsListRenderer.RecordRow";
    static components = Object.assign({}, ListRenderer.components, {
        PrescriptionsInspector,
        PrescriptionsListRendererCheckBox,
        FileUploadProgressContainer,
        FileUploadProgressDataRow,
        PrescriptionsDropZone,
        PrescriptionsActionHelper,
        PrescriptionsFileViewer,
    });

    setup() {
        super.setup();
        this.root = useRef("root");
        const { uploads } = useService("file_upload");
        this.prescriptionUploads = uploads;
        useCommand(
            _t("Select all"),
            () => {
                const allSelected =
                    this.props.list.selection.length === this.props.list.records.length;
                this.props.list.records.forEach((record) => {
                    record.toggleSelection(!allSelected);
                });
            },
            {
                category: "smart_action",
                hotkey: "control+a",
            }
        );
    }

    getDocumentsAttachmentViewerProps() {
        return { previewStore: this.props.previewStore };
    }

    getDocumentsInspectorProps() {
        return {
            prescriptions: this.props.inspectedPrescriptions.length
                ? this.props.inspectedPrescriptions
                : this.props.list.selection,
            count: this.props.list.model.useSampleModel ? 0 : this.props.list.count,
            fileSize: this.props.list.model.fileSize,
            fields: this.props.list.fields,
            archInfo: this.props.archInfo,
        };
    }

    /**
     * Called when a keydown event is triggered.
     */
    onGlobalKeydown(ev) {
        if (ev.key !== "Enter" && ev.key !== " ") {
            return;
        }
        const row = ev.target.closest(".o_data_row");
        const record = row && this.props.list.records.find((rec) => rec.id === row.dataset.id);
        if (!record) {
            return;
        }
        const options = {};
        if (ev.key === " ") {
            options.isKeepSelection = true;
        }
        ev.stopPropagation();
        ev.preventDefault();
        record.onRecordClick(ev, options);
    }

    /**
     * There's a custom behavior on cell clicked as we (un)select the row (see record.onRecordClick)
     */
    onCellClicked() {}

    /**
     * Called when a click event is triggered.
     */
    onGlobalClick(ev) {
        // We have to check that we are indeed clicking in the list view as on mobile,
        // the inspector renders above the renderer but it still triggers this event.
        if (ev.target.closest(".o_data_row") || !ev.target.closest(".o_list_renderer")) {
            return;
        }
        this.props.list.selection.forEach((el) => el.toggleSelection(false));
    }

    get hasSelectors() {
        return this.props.allowSelectors;
    }
}
