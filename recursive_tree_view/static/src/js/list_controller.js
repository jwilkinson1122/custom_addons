/** @odoo-module **/

import { ListController } from '@web/views/list/list_controller';
import { patch } from '@web/core/utils/patch';
import { useBus } from "@web/core/utils/hooks";

patch(ListController.prototype, {
    async setup() {
        if (this.props.archInfo.recursive) {
            this.recursive = true;
            useBus(this.env.bus, "recursive:reparent", this.onReparent);
        } else {
            this.recursive = false;
        }
        super.setup();
    },

    async onReparent({ draggedId, targetId, sameParent }) {
        const method = sameParent ? 'reorder_node' : 'reparent_node';
        await this.orm.call('product.options', method, [draggedId, targetId]);
        this.model.load();
    },

    get modelParams() {
        const params = super.modelParams;
        if (this.recursive) {
            params["config"]["recursive"] = true;
        }
        return params;
    },
});
