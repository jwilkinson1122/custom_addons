odoo.define('prescription.PrescriptionKanbanRenderer', function (require) {
"use strict";

/**
 * This file defines the Renderer for the Prescription Kanban view, which is an
 * override of the KanbanRenderer.
 */

var PrescriptionKanbanRecord = require('prescription.PrescriptionKanbanRecord');

var KanbanRenderer = require('web.KanbanRenderer');

var PrescriptionKanbanRenderer = KanbanRenderer.extend({
    config: _.extend({}, KanbanRenderer.prototype.config, {
        KanbanRecord: PrescriptionKanbanRecord,
    }),

    /**
     * @override
     */
    start: function () {
        this.$el.addClass('o_prescription_view o_prescription_kanban_view position-relative align-content-start flex-grow-1 flex-shrink-1');
        return this._super.apply(this, arguments);
    },
});

return PrescriptionKanbanRenderer;

});
