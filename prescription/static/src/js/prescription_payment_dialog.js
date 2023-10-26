odoo.define('prescription.PrescriptionPaymentDialog', function (require) {
"use strict";

var Dialog = require('web.Dialog');

var PrescriptionPaymentDialog = Dialog.extend({
    template: 'prescription.PrescriptionPaymentDialog',

    init: function (parent, options) {
        this._super.apply(this, arguments);

        options = options || {};

        this.message = options.message || '';
    },
});

return PrescriptionPaymentDialog;

});
