odoo.define('prescription.PrescriptionKanbanView', function (require) {
"use strict";

var PrescriptionKanbanController = require('prescription.PrescriptionKanbanController');
var PrescriptionKanbanRenderer = require('prescription.PrescriptionKanbanRenderer');

var core = require('web.core');
var KanbanView = require('web.KanbanView');
var view_registry = require('web.view_registry');

var _lt = core._lt;

var PrescriptionKanbanView = KanbanView.extend({
    config: _.extend({}, KanbanView.prototype.config, {
        Controller: PrescriptionKanbanController,
        Renderer: PrescriptionKanbanRenderer,
    }),
    display_name: _lt('Prescription Kanban'),

    /**
     * @override
     */
    _createSearchModel(params, extraExtensions = {}) {
        Object.assign(extraExtensions, { Prescription: {} });
        return this._super(params, extraExtensions);
    },
});

view_registry.add('prescription_kanban', PrescriptionKanbanView);

return PrescriptionKanbanView;

});
