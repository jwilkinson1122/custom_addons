/** @odoo-module **/

import { ListRenderer } from '@web/views/list/list_renderer';
import { patch } from '@web/core/utils/patch';
import { RecursiveRecordRow } from "./recursive_record_row";

patch(ListRenderer.prototype, {
    setup() {
        super.setup();
        this.recursive = this.props.archInfo.recursive;
    },

    get recordRowComponent() {
        return this.recursive ? RecursiveRecordRow : this.constructor.components.RecordRow;
    },

    getRowProps(record) {
        const props = super.getRowProps(record);
        if (this.recursive) {
            props.onReparent = (draggedId, targetId) => {
                const dragged = this.props.list.records.find(r => r.resId === draggedId);
                const target = this.props.list.records.find(r => r.resId === targetId);
                const sameParent = dragged.parent?.resId === target.parent?.resId;

                this.env.bus.trigger("recursive:reparent", {
                    draggedId,
                    targetId,
                    sameParent,
                });
            };
        }
        return props;
    },
});
