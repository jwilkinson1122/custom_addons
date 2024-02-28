/** @odoo-module **/

import { ActivityRenderer } from "@mail/views/web/activity/activity_renderer";

import { PrescriptionsInspector } from "../inspector/prescriptions_inspector";
import { PrescriptionsFileViewer } from "../helper/prescriptions_file_viewer";

import { useRef } from "@odoo/owl";

export class PrescriptionsActivityRenderer extends ActivityRenderer {
    static props = {
        ...ActivityRenderer.props,
        inspectedPrescriptions: Array,
        previewStore: Object,
    };
    static template = "prescriptions.PrescriptionsActivityRenderer";
    static components = {
        ...ActivityRenderer.components,
        PrescriptionsFileViewer,
        PrescriptionsInspector,
    };

    setup() {
        super.setup();
        this.root = useRef("root");
    }

    getPrescriptionsAttachmentViewerProps() {
        return { previewStore: this.props.previewStore };
    }

    /**
     * Props for prescriptionsInspector
     */
    getPrescriptionsInspectorProps() {
        return {
            prescriptions: this.props.records.filter((rec) => rec.selected),
            count: 0,
            fileSize: 0,
            archInfo: this.props.archInfo,
        };
    }
}
