odoo.define('pod_erp.models', function(require){

    var models = require('point_of_sale.models');

    models.load_models([{
        model:  'podiatry.practitioner',
        fields: ['name'],
        loaded: function(self,practitioners){
            self.podiatry = {};
            self.podiatry.practitioners = practitioners;
        },
    },{
        model:  'prescription',
        loaded: function(self,podiatry_orders){
            self.podiatry.all_orders = podiatry_orders;
            self.podiatry.order_by_id = {};
            podiatry_orders.forEach(function(order){
                self.podiatry.order_by_id[order.id] = order;
            });
        },
    },{
        model:  'eye.test.type',
        fields: ['name'],
        loaded: function(self,test_type){
            self.podiatry.test_type = test_type;
        },
    },{
// =====================================
//  To select all podiatry attributes ids
// =====================================
        model:  'product.attribute',
        domain: [['in_pos','=','true']],
        loaded: function(self,attributes){
            self.podiatry.product_attributes_by_id = {};
            self.podiatry.product_attributes =  _.sortBy( attributes, 'Sequence');
            for (var i=0;i< attributes.length;i++)
                self.podiatry.product_attributes_by_id[attributes[i].id] = attributes[i];
        },
    },{
// ========================================
//  To select all template attributes lines
// ========================================
        model:  'product.template.attribute.line',
//        fields: ['id','attribute_id'],
        loaded: function(self,attributes){
            self.podiatry.product_attributes_lines_by_id = {};
            attributes.forEach(function(attribute){
                self.podiatry.product_attributes_lines_by_id[attribute.id] = attribute;
            });
        },
    }]);
    models.load_models([{
// =============================================
//  To select all products with podiatry variants
// =============================================
        model:  'product.template',
        fields: ['id','name', 'attribute_line_ids','product_variant_count','product_variant_ids'],
        loaded: function(self,product_templates){
            self.podiatry.glasses = [];
            self.podiatry.glasses_by_id = {};
            self.podiatry.glasses = product_templates.filter(function(el){return el.product_variant_count > 1});
            self.podiatry.glasses.forEach(function(podiatry_glass){
                self.podiatry.glasses_by_id[podiatry_glass.id] = podiatry_glass;
            });
        },
    },{
        model:  'product.attribute.value',
        loaded: function(self,attributes){
            self.podiatry.product_attribute_values_by_id = {};
            self.podiatry.product_attribute_values= attributes;
            attributes.forEach(function(attribute){
                self.podiatry.product_attribute_values_by_id[attribute.id] = attribute;
            });
            self.podiatry.product_attributes_for_xml = [];
            i = 0;
            self.podiatry.product_attributes.forEach(function(attribute){
                self.podiatry.product_attributes_for_xml[i] = {};
                self.podiatry.product_attributes_for_xml[i].name = attribute.name;
                self.podiatry.product_attributes_for_xml[i].attributes = [];
                attribute.value_ids.forEach(function(attribute_value_id){
                    self.podiatry.product_attributes_for_xml[i].attributes.push(self.podiatry.product_attribute_values_by_id[attribute_value_id].name);
                })
                i++;
            });
            ceil = Math.ceil(self.podiatry.product_attributes_for_xml.length / 4);
            floor = Math.floor(self.podiatry.product_attributes_for_xml.length / 4);
            self.podiatry.variants1 = self.podiatry.product_attributes_for_xml.slice(0, ceil);
            if(self.podiatry.product_attributes_for_xml.length % 4 == 2){
                self.podiatry.variants2 = self.podiatry.product_attributes_for_xml.slice(ceil, ceil+ceil);
                self.podiatry.variants3 = self.podiatry.product_attributes_for_xml.slice(ceil+ceil, ceil+ceil+floor);
                self.podiatry.variants4 = self.podiatry.product_attributes_for_xml.slice(ceil+ceil+floor);
            }
            else if (self.podiatry.product_attributes_for_xml.length % 4 == 3){
                self.podiatry.variants2 = self.podiatry.product_attributes_for_xml.slice(ceil, ceil+ceil);
                self.podiatry.variants3 = self.podiatry.product_attributes_for_xml.slice(ceil+ceil, ceil+ceil+ceil);
                self.podiatry.variants4 = self.podiatry.product_attributes_for_xml.slice(ceil+ceil+ceil);
            }
            else{
                self.podiatry.variants2 = self.podiatry.product_attributes_for_xml.slice(ceil, ceil+floor);
                self.podiatry.variants3 = self.podiatry.product_attributes_for_xml.slice(ceil+floor, ceil+floor+floor);
                self.podiatry.variants4 = self.podiatry.product_attributes_for_xml.slice(ceil+floor+floor);
            }
        },
    }]);


    models.load_fields("pos.order", ['podiatry_reference']);
    var _super_order = models.Order.prototype;

    models.Order = models.Order.extend({
        init_from_JSON: function (json) {
            var res = _super_order.init_from_JSON.apply(this, arguments);
            if (json.podiatry_reference) {
                var podiatry_reference = this.pos.podiatry.order_by_id[json.podiatry_reference];
                if (podiatry_reference) {
                    this.set_podiatry_reference(podiatry_reference);
                }
            }
            return res;
        },
        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.apply(this, arguments);
            if (this.podiatry_reference) {
                if (this.podiatry_reference[0])
                    json.podiatry_reference=this.podiatry_reference[0];
                else
                    json.podiatry_reference = this.podiatry_reference.id;
            }
            return json;
        },
        set_podiatry_reference: function (podiatry_reference) {
            this.podiatry_reference = podiatry_reference;
            this.trigger('change', this);
        },
    });

    models.PosModel = models.PosModel.extend({
        get_podiatry_reference: function() {
            var order = this.get_order();
            if (order.podiatry_reference) {
                podiatry_reference = this.podiatry.order_by_id[order.podiatry_reference.id]
                return podiatry_reference;
            }
            return null;
        },
        delete_current_order: function(){
            var order = this.get_order();
            if (order) {
                order.destroy({'reason':'abandon'});
            }
            $('.podiatry_prescription').text("Prescription")
        },
    });



});