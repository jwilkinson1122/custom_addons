odoo.define('pod_erp.models', function (require) {

    var models = require('point_of_sale.models');

    models.load_models([{
        model: 'pod.practitioner',
        fields: ['name'],
        loaded: function (self, practitioners) {
            self.pod = {};
            self.pod.practitioners = practitioners;
        },
    }, {
        model: 'practitioner.prescription',
        loaded: function (self, pod_orders) {
            self.pod.all_orders = pod_orders;
            self.pod.order_by_id = {};
            pod_orders.forEach(function (order) {
                self.pod.order_by_id[order.id] = order;
            });
        },
    }, {
        model: 'eye.test.type',
        fields: ['name'],
        loaded: function (self, test_type) {
            self.pod.test_type = test_type;
        },
    }, {
        // =====================================
        //  To select all pod attributes ids
        // =====================================
        model: 'product.attribute',
        domain: [['in_pos', '=', 'true']],
        loaded: function (self, attributes) {
            self.pod.product_attributes_by_id = {};
            self.pod.product_attributes = _.sortBy(attributes, 'Sequence');
            for (var i = 0; i < attributes.length; i++)
                self.pod.product_attributes_by_id[attributes[i].id] = attributes[i];
        },
    }, {
        // ========================================
        //  To select all template attributes lines
        // ========================================
        model: 'product.template.attribute.line',
        //        fields: ['id','attribute_id'],
        loaded: function (self, attributes) {
            self.pod.product_attributes_lines_by_id = {};
            attributes.forEach(function (attribute) {
                self.pod.product_attributes_lines_by_id[attribute.id] = attribute;
            });
        },
    }]);
    models.load_models([{
        // =============================================
        //  To select all products with pod variants
        // =============================================
        model: 'product.template',
        fields: ['id', 'name', 'attribute_line_ids', 'product_variant_count', 'product_variant_ids'],
        loaded: function (self, product_templates) {
            self.pod.glasses = [];
            self.pod.glasses_by_id = {};
            self.pod.glasses = product_templates.filter(function (el) { return el.product_variant_count > 1 });
            self.pod.glasses.forEach(function (pod_glass) {
                self.pod.glasses_by_id[pod_glass.id] = pod_glass;
            });
        },
    }, {
        model: 'product.attribute.value',
        loaded: function (self, attributes) {
            self.pod.product_attribute_values_by_id = {};
            self.pod.product_attribute_values = attributes;
            attributes.forEach(function (attribute) {
                self.pod.product_attribute_values_by_id[attribute.id] = attribute;
            });
            self.pod.product_attributes_for_xml = [];
            i = 0;
            self.pod.product_attributes.forEach(function (attribute) {
                self.pod.product_attributes_for_xml[i] = {};
                self.pod.product_attributes_for_xml[i].name = attribute.name;
                self.pod.product_attributes_for_xml[i].attributes = [];
                attribute.value_ids.forEach(function (attribute_value_id) {
                    self.pod.product_attributes_for_xml[i].attributes.push(self.pod.product_attribute_values_by_id[attribute_value_id].name);
                })
                i++;
            });
            ceil = Math.ceil(self.pod.product_attributes_for_xml.length / 4);
            floor = Math.floor(self.pod.product_attributes_for_xml.length / 4);
            self.pod.variants1 = self.pod.product_attributes_for_xml.slice(0, ceil);
            if (self.pod.product_attributes_for_xml.length % 4 == 2) {
                self.pod.variants2 = self.pod.product_attributes_for_xml.slice(ceil, ceil + ceil);
                self.pod.variants3 = self.pod.product_attributes_for_xml.slice(ceil + ceil, ceil + ceil + floor);
                self.pod.variants4 = self.pod.product_attributes_for_xml.slice(ceil + ceil + floor);
            }
            else if (self.pod.product_attributes_for_xml.length % 4 == 3) {
                self.pod.variants2 = self.pod.product_attributes_for_xml.slice(ceil, ceil + ceil);
                self.pod.variants3 = self.pod.product_attributes_for_xml.slice(ceil + ceil, ceil + ceil + ceil);
                self.pod.variants4 = self.pod.product_attributes_for_xml.slice(ceil + ceil + ceil);
            }
            else {
                self.pod.variants2 = self.pod.product_attributes_for_xml.slice(ceil, ceil + floor);
                self.pod.variants3 = self.pod.product_attributes_for_xml.slice(ceil + floor, ceil + floor + floor);
                self.pod.variants4 = self.pod.product_attributes_for_xml.slice(ceil + floor + floor);
            }
        },
    }]);


    models.load_fields("pos.order", ['pod_reference']);
    var _super_order = models.Order.prototype;

    models.Order = models.Order.extend({
        init_from_JSON: function (json) {
            var res = _super_order.init_from_JSON.apply(this, arguments);
            if (json.pod_reference) {
                var pod_reference = this.pos.pod.order_by_id[json.pod_reference];
                if (pod_reference) {
                    this.set_pod_reference(pod_reference);
                }
            }
            return res;
        },
        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.apply(this, arguments);
            if (this.pod_reference) {
                if (this.pod_reference[0])
                    json.pod_reference = this.pod_reference[0];
                else
                    json.pod_reference = this.pod_reference.id;
            }
            return json;
        },
        set_pod_reference: function (pod_reference) {
            this.pod_reference = pod_reference;
            this.trigger('change', this);
        },
    });

    models.PosModel = models.PosModel.extend({
        get_pod_reference: function () {
            var order = this.get_order();
            if (order.pod_reference) {
                pod_reference = this.pod.order_by_id[order.pod_reference.id]
                return pod_reference;
            }
            return null;
        },
        delete_current_order: function () {
            var order = this.get_order();
            if (order) {
                order.destroy({ 'reason': 'abandon' });
            }
            $('.pod_prescription').text("Prescription")
        },
    });



});