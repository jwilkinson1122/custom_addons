odoo.define('prescription.PrescriptionKanbanRecord', function (require) {
    "use strict";

    /**
     * This file defines the KanbanRecord for the Prescription Kanban view.
     */

    var KanbanRecord = require('web.KanbanRecord');

    var PrescriptionKanbanRecord = KanbanRecord.extend({
        events: _.extend({}, KanbanRecord.prototype.events, {
            'click': '_onSelectRecord',
        }),

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * Open the add product wizard
         *
         * @private
         * @param {MouseEvent} ev Click event
         */
        _onSelectRecord: function (ev) {
            ev.preventDefault();
            // ignore clicks on oe_kanban_action elements
            if (!$(ev.target).hasClass('oe_kanban_action')) {
                this.trigger_up('open_wizard', {productId: this.recordData.product_id ? this.recordData.product_id.res_id: this.recordData.id});
            }
        },

        _openRecord() {},
    });

    return PrescriptionKanbanRecord;

    });
