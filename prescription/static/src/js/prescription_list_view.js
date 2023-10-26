odoo.define('prescription.PrescriptionListView', function (require) {
"use strict";

var PrescriptionListController = require('prescription.PrescriptionListController');
var PrescriptionListRenderer = require('prescription.PrescriptionListRenderer');

var core = require('web.core');
var ListView = require('web.ListView');
var view_registry = require('web.view_registry');

var _lt = core._lt;

var PrescriptionListView = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
        Controller: PrescriptionListController,
        Renderer: PrescriptionListRenderer,
    }),
    display_name: _lt('Prescription List'),

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _createSearchModel(params, extraExtensions = {}) {
        Object.assign(extraExtensions, { Prescription: {} });
        return this._super(params, extraExtensions);
    },

});

view_registry.add('prescription_list', PrescriptionListView);

return PrescriptionListView;

});
