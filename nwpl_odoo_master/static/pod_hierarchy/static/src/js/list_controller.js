/** @odoo-module **/

import {ListController} from '@web/views/list/list_controller';
import {patch} from '@web/core/utils/patch';
import {useBus} from "@web/core/utils/hooks";

patch(ListController.prototype, {
    async setup() {
        if (this.props.archInfo.recursive) {
            this.recursive = true;
            useBus(this.env.bus, "expand-collapse-parent", this.onExpandCollapseParent);
        } else {
            this.recursive = false;
        }
        super.setup();
    },

    async onExpandCollapseParent(ev) {
        const parentId = ev.detail;
        const parentRecord = this.model.findRecordInHierarchy(parentId);

        if (!parentRecord) return;

        if (parentRecord.expanded) {
            // Collapse the node
            parentRecord.expanded = false;
        } else {
            // Expand the node and fetch children if not already fetched
            if (!parentRecord.childrenFetched) {
                await this.model._loadChildren([parentRecord], this.model.config);
            }
            parentRecord.expanded = true;
        }

        // Trigger UI update
        this.render();
    },

    get modelParams() {
        const params = super.modelParams;
        if (this.recursive) {
            params["config"]["recursive"] = true;
        }
        return params;
    },

});
