odoo.define('podiatry_erp.ReceiptScreen', function(require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const ClientListScreen = require('point_of_sale.ClientListScreen');
    var models = require('point_of_sale.models');
    var _super_order = models.Order.prototype;

    models.Order = models.Order.extend({
        export_for_printing: function () {
            var result = _super_order.export_for_printing.apply(this, arguments);

            if (this.podiatry_reference){
                if (this.podiatry_reference.id)
                    result.podiatry_order = this.pos.podiatry.order_by_id[this.podiatry_reference.id]
                else
                    result.podiatry_order = this.pos.podiatry.order_by_id[this.podiatry_reference]
            }
            return result;
        },

        saved_amount: function() {
        }
    });

});