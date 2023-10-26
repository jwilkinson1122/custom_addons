odoo.define('prescription.PrescriptionListController', function (require) {
"use strict";

/**
 * This file defines the Controller for the Prescription List view, which is an
 * override of the ListController.
 */

var ListController = require('web.ListController');
var PrescriptionControllerCommon = require('prescription.PrescriptionControllerCommon');

var PrescriptionListController = ListController.extend(PrescriptionControllerCommon, {
    custom_events: _.extend({}, ListController.prototype.custom_events, PrescriptionControllerCommon.custom_events),
});

return PrescriptionListController;

});
