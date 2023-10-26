odoo.define('prescription.PrescriptionKanbanController', function (require) {
"use strict";

/**
 * This file defines the Controller for the Prescription Kanban view, which is an
 * override of the KanbanController.
 */

var KanbanController = require('web.KanbanController');
var PrescriptionControllerCommon = require('prescription.PrescriptionControllerCommon');

var PrescriptionKanbanController = KanbanController.extend(PrescriptionControllerCommon , {
    custom_events: _.extend({}, KanbanController.prototype.custom_events, PrescriptionControllerCommon.custom_events),
});

return PrescriptionKanbanController;

});
