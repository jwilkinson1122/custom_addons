/** @odoo-module **/

import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";

patch(KanbanRenderer.prototype, {
    setup() {
        super.setup();
        this.recursive = !!this.props.archInfo.recursive; // Ensure boolean
        this.state = useState({ expanded: {} }); // Track expanded nodes
    },

    async toggleExpand(record) {
        try {
            if (!record.expanded && !record.childrenFetched) {
                await this.props.model._loadChildren([record], this.props.config);
            }
            record.expanded = !record.expanded;
            this.state = { ...this.state };
        } catch (error) {
            console.error("Error while toggling expand:", error);
        }
    },

    render() {
        const records = this.props.list.records;
        return records.map((record) => this._renderRecord(record));
    },

    _renderRecord(record) {
        const isExpanded = record.expanded;

        return (
            <div className={`o_kanban_record ${isExpanded ? "expanded" : "collapsed"}`}>
                <button onClick={() => this.toggleExpand(record)}>
                    {isExpanded ? "▼" : "▶"}
                </button>
                <div>{record.data.name || "Unnamed"}</div>
                {isExpanded && Array.isArray(record.children) && (
                    <div className="o_kanban_children">
                        {record.children.map((child) => this._renderRecord(child))}
                    </div>
                )}
            </div>
        );
    },
});
