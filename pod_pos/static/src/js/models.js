odoo.define('pod_pos.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var utils = require('web.utils');
    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;
    
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        set_modifier_attribute_list:function(modifier_attribute_list){
            this.modifier_attribute_list = modifier_attribute_list 
        },
        get_modifier_attribute_list: function(){
            return this.modifier_attribute_list;
        },

        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.modifier_attribute_list = this.modifier_attribute_list || false;
            return json;
        },
        
        init_from_JSON: function(json){
            _super_order.init_from_JSON.apply(this,arguments);
            this.modifier_attribute_list = json.modifier_attribute_list;
            
        },  
        
    });


    var OrderlineSuper = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({

        initialize: function(attr, options) {
            this.is_modifier = this.is_modifier || "";
            this.is_pieces = this.is_pieces;
            OrderlineSuper.initialize.call(this,attr,options);
        },
        set_modifier: function(is_modifier){
    
            this.is_modifier = is_modifier;
            if (this.is_modifier){
                this.set_modifier_price(this.product.lst_price);
            }
            this.trigger('change',this);
        },

        set_unit_price: function(price){
            this.order.assert_editable();
            if(this.product.orthotic_pieces)
            {
                this.is_pieces = true;
                var total = price;   
                this.price = round_di(parseFloat(total) || 0, this.pos.dp['Product Price']);
            }
            else{
                this.price = round_di(parseFloat(price) || 0, this.pos.dp['Product Price']);
            }
            this.trigger('change',this);
        },

        set_modifier_price: function(price){
            var prods = this.get_modifier()
            var total = price;
            prods.forEach(function (prod) {
                if(prod)
                {
                    
                    if(prod.portion_type == "full"){
                        total += (prod.lst_price * prod.qty) 
                    }

                    if(prod.portion_type == "half"){
                        var value = (prod.lst_price/2) * prod.qty 
                        total += value;
                    }

                    if(prod.portion_type == "quater"){
                        total += (prod.lst_price/4) * prod.qty 
                    }

                    if(prod.is_sub){
                        total += (prod.lst_price * prod.qty)
                    }
                }   
            });
            this.set_unit_price(total);
            
            this.trigger('change',this);
        },

        get_modifier: function(){
            if(this.product.orthotic_pieces)
            {
                this.is_pieces = true;
            }
            return this.is_modifier
        },

        export_for_printing: function(){
            var json = OrderlineSuper.export_for_printing.call(this);
            json.is_modifier = this.get_modifier();
            return json;
        },

        export_as_JSON: function() {
            var json = OrderlineSuper.export_as_JSON.apply(this,arguments);
            json.is_modifier = this.get_modifier() || false;
            json.is_pieces = this.is_pieces || false;
            return json;
        },
        
        init_from_JSON: function(json){
            OrderlineSuper.init_from_JSON.apply(this,arguments);
            this.is_modifier = json.is_modifier;
            this.is_pieces = json.is_pieces;
            

        },
    });
});
