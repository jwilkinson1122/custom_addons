odoo.define('optical_erp.models', function(require){

    var models = require('point_of_sale.models');

    models.load_models([{
        model:  'optical.dr',
        fields: ['name'],
        loaded: function(self,doctors){
            self.optical = {};
            self.optical.doctors = doctors;
        },
    },{
        model:  'dr.prescription',
        loaded: function(self,optical_orders){
            self.optical.all_orders = optical_orders;
            self.optical.order_by_id = {};
            optical_orders.forEach(function(order){
                self.optical.order_by_id[order.id] = order;
            });
        },
    },{
        model:  'eye.test.type',
        fields: ['name'],
        loaded: function(self,test_type){
            self.optical.test_type = test_type;
        },
    },{
// =====================================
//  To select all optical attributes ids
// =====================================
        model:  'product.attribute',
        domain: [['in_pos','=','true']],
        loaded: function(self,attributes){
            self.optical.product_attributes_by_id = {};
            self.optical.product_attributes =  _.sortBy( attributes, 'Sequence');
            for (var i=0;i< attributes.length;i++)
                self.optical.product_attributes_by_id[attributes[i].id] = attributes[i];
        },
    },{
// ========================================
//  To select all template attributes lines
// ========================================
        model:  'product.template.attribute.line',
//        fields: ['id','attribute_id'],
        loaded: function(self,attributes){
            self.optical.product_attributes_lines_by_id = {};
            attributes.forEach(function(attribute){
                self.optical.product_attributes_lines_by_id[attribute.id] = attribute;
            });
        },
    }]);
    models.load_models([{
// =============================================
//  To select all products with optical variants
// =============================================
        model:  'product.template',
        fields: ['id','name', 'attribute_line_ids','product_variant_count','product_variant_ids'],
        loaded: function(self,product_templates){
            self.optical.glasses = [];
            self.optical.glasses_by_id = {};
            self.optical.glasses = product_templates.filter(function(el){return el.product_variant_count > 1});
            self.optical.glasses.forEach(function(optical_glass){
                self.optical.glasses_by_id[optical_glass.id] = optical_glass;
            });
        },
    },{
        model:  'product.attribute.value',
        loaded: function(self,attributes){
            self.optical.product_attribute_values_by_id = {};
            self.optical.product_attribute_values= attributes;
            attributes.forEach(function(attribute){
                self.optical.product_attribute_values_by_id[attribute.id] = attribute;
            });
            self.optical.product_attributes_for_xml = [];
            i = 0;
            self.optical.product_attributes.forEach(function(attribute){
                self.optical.product_attributes_for_xml[i] = {};
                self.optical.product_attributes_for_xml[i].name = attribute.name;
                self.optical.product_attributes_for_xml[i].attributes = [];
                attribute.value_ids.forEach(function(attribute_value_id){
                    self.optical.product_attributes_for_xml[i].attributes.push(self.optical.product_attribute_values_by_id[attribute_value_id].name);
                })
                i++;
            });
            ceil = Math.ceil(self.optical.product_attributes_for_xml.length / 4);
            floor = Math.floor(self.optical.product_attributes_for_xml.length / 4);
            self.optical.variants1 = self.optical.product_attributes_for_xml.slice(0, ceil);
            if(self.optical.product_attributes_for_xml.length % 4 == 2){
                self.optical.variants2 = self.optical.product_attributes_for_xml.slice(ceil, ceil+ceil);
                self.optical.variants3 = self.optical.product_attributes_for_xml.slice(ceil+ceil, ceil+ceil+floor);
                self.optical.variants4 = self.optical.product_attributes_for_xml.slice(ceil+ceil+floor);
            }
            else if (self.optical.product_attributes_for_xml.length % 4 == 3){
                self.optical.variants2 = self.optical.product_attributes_for_xml.slice(ceil, ceil+ceil);
                self.optical.variants3 = self.optical.product_attributes_for_xml.slice(ceil+ceil, ceil+ceil+ceil);
                self.optical.variants4 = self.optical.product_attributes_for_xml.slice(ceil+ceil+ceil);
            }
            else{
                self.optical.variants2 = self.optical.product_attributes_for_xml.slice(ceil, ceil+floor);
                self.optical.variants3 = self.optical.product_attributes_for_xml.slice(ceil+floor, ceil+floor+floor);
                self.optical.variants4 = self.optical.product_attributes_for_xml.slice(ceil+floor+floor);
            }
        },
    }]);


    models.load_fields("pos.order", ['optical_reference']);
    var _super_order = models.Order.prototype;

    models.Order = models.Order.extend({
        init_from_JSON: function (json) {
            var res = _super_order.init_from_JSON.apply(this, arguments);
            if (json.optical_reference) {
                var optical_reference = this.pos.optical.order_by_id[json.optical_reference];
                if (optical_reference) {
                    this.set_optical_reference(optical_reference);
                }
            }
            return res;
        },
        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.apply(this, arguments);
            if (this.optical_reference) {
                if (this.optical_reference[0])
                    json.optical_reference=this.optical_reference[0];
                else
                    json.optical_reference = this.optical_reference.id;
            }
            return json;
        },
        set_optical_reference: function (optical_reference) {
            this.optical_reference = optical_reference;
            this.trigger('change', this);
        },
    });

    models.PosModel = models.PosModel.extend({
        get_optical_reference: function() {
            var order = this.get_order();
            if (order.optical_reference) {
                optical_reference = this.optical.order_by_id[order.optical_reference.id]
                return optical_reference;
            }
            return null;
        },
        delete_current_order: function(){
            var order = this.get_order();
            if (order) {
                order.destroy({'reason':'abandon'});
            }
            $('.optical_prescription').text("Prescription")
        },
    });



});