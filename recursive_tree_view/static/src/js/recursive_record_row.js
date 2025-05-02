/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

/**
 * Recursive Tree Row Component with Expand/Collapse and Drag Support
 */
export class RecursiveRecordRow extends Component {
    static props = {
        record: Object,
        onReparent: { type: Function, optional: true },
        recursive: { type: Boolean, optional: true },
        depth: { type: Number, optional: true },
    };

    static template = "recursive_tree_view.RecordRow";

    setup() {
        this.state = useState({
            isHover: false,
            expanded: this.props.record.expanded ?? false,
        });
    }

    // Drag/Drop Handlers
    onDragStart(ev) {
        ev.dataTransfer.effectAllowed = "move";
        ev.dataTransfer.setData("x/product_option_drag", this.props.record.resId);
    }

    onDrop(ev) {
        ev.preventDefault();
        this.state.isHover = false;

        if (!ev.dataTransfer.types.includes("x/product_option_drag")) return;
        const draggedId = ev.dataTransfer.getData("x/product_option_drag");
        if (draggedId === this.props.record.resId) return;

        this.props.onReparent?.(draggedId, this.props.record.resId);
    }

    onDragEnter(ev) {
        ev.preventDefault();
        this.state.isHover = true;
    }

    onDragLeave(ev) {
        this.state.isHover = false;
    }

    onToggleExpand() {
        this.state.expanded = !this.state.expanded;
    }

    get rowClasses() {
        return {
            "o_dragging": this.state.isHover,
        };
    }
}