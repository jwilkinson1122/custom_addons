odoo.define('podiatry.podiatry_kanban', function (require) {
    'use strict';

    const KanbanRecord = require('web.KanbanRecord');

    KanbanRecord.include({

        /**
         * @override
         * @private
         */
        _openRecord() {
            if (this.modelName === 'podiatry.device.model.line' && this.$(".oe_kanban_podiatry_model").length) {
                this.$('.oe_kanban_podiatry_model').first().click();
            } else {
                this._super.apply(this, arguments);
            }
        },
    });
});
