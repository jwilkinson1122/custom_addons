/** @odoo-module **/

import ProductKanbanRecord from "@pod_hms/js/product_kanbanrecord";
import KanbanRenderer from "web.KanbanRenderer";

const ProductKanbanRenderer = KanbanRenderer.extend({
    config: _.extend({}, KanbanRenderer.prototype.config, {
        KanbanRecord: ProductKanbanRecord,
    }),
    /*
     * Re-write to keep selected products when switching between pages and filters
    */
    updateSelection: function (selectedRecords) {
        _.each(this.widgets, function (widget) {
            var selected = _.contains(selectedRecords, widget.id);
            widget._updateRecordView(selected);
        });
    },
});


export default ProductKanbanRenderer;
