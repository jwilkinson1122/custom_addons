odoo.define('pod_erp.ReceiptScreen', function(require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const ClientListScreen = require('point_of_sale.ClientListScreen');
    var models = require('point_of_sale.models');
    var _super_order = models.Order.prototype;

    models.Order = models.Order.extend({
        export_for_printing: function () {
            var result = _super_order.export_for_printing.apply(this, arguments);

            if (this.pod_reference){
                if (this.pod_reference.id)
                    result.pod_order = this.pos.pod.order_by_id[this.pod_reference.id]
                else
                    result.pod_order = this.pos.pod.order_by_id[this.pod_reference]
            }
            return result;
        },

        saved_amount: function() {
        }
    });

});