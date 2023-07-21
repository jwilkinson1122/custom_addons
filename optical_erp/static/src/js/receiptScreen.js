odoo.define('optical_erp.ReceiptScreen', function(require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const ClientListScreen = require('point_of_sale.ClientListScreen');
    var models = require('point_of_sale.models');
    var _super_order = models.Order.prototype;

    models.Order = models.Order.extend({
        export_for_printing: function () {
            var result = _super_order.export_for_printing.apply(this, arguments);

            if (this.optical_reference){
                if (this.optical_reference.id)
                    result.optical_order = this.pos.optical.order_by_id[this.optical_reference.id]
                else
                    result.optical_order = this.pos.optical.order_by_id[this.optical_reference]
            }
            return result;
        },

        saved_amount: function() {
        }
    });

});