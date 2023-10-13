odoo.define('pod_order_management.model', function (require) {
    'use strict';

    var ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');
    models.load_fields('res.partner', ['info_ids']);


    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend
        ({
            initialize: function (attr, options) {
                _super_orderline.initialize.call(this, attr, options);
                this.product_variants = this.product_variants || [];
            },
            init_from_JSON: function (json) {
                _super_orderline.init_from_JSON.apply(this, arguments);
                this.product_variants = json.product_variants || [];
            },
            export_as_JSON: function () {
                var json = _super_orderline.export_as_JSON.apply(this, arguments);
                json.product_variants = this.product_variants || [];
                return json;
            },
            export_for_printing: function () {
                var line = _super_orderline.export_for_printing.apply(this, arguments);
                line.product_variants = this.product_variants;
                console.log(line, "line")
                return line;
            },
        });

    models.load_models({
        model: 'res.partner.info',
        fields: ['name', 'info_name', 'partner_id', 'field_id'],
        domain: null,
        loaded: function (self, info) {
            self.more_info = info;
        },
    });
    models.load_models({
        model: 'custom.partner.field',
        fields: [],
        domain: function (self) {
            return [
                ['id', 'in', self.config.show_custom_partner_field]
            ];
        },
        loaded: function (self, field) {
            self.custom_field = field;
        },
    });

    // var _super_orderline = models.Orderline.prototype;
    // models.Orderline = models.Orderline.extend
    //     ({
    //         initialize: function (attr, options) {
    //             _super_orderline.initialize.call(this, attr, options);
    //             this.product_variants = this.product_variants || [];
    //         },
    //         init_from_JSON: function (json) {
    //             _super_orderline.init_from_JSON.apply(this, arguments);
    //             this.product_variants = json.product_variants || [];
    //         },
    //         export_as_JSON: function () {
    //             var json = _super_orderline.export_as_JSON.apply(this, arguments);
    //             json.product_variants = this.product_variants || [];
    //             return json;
    //         },
    //         export_for_printing: function () {
    //             var line = _super_orderline.export_for_printing.apply(this, arguments);
    //             line.product_variants = this.product_variants;
    //             console.log(line, "line")
    //             return line;
    //         },
    //     });

});