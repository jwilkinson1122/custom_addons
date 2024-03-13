/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Order, Orderline, Product } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { roundDecimals as round_di } from "@web/core/utils/numbers";
import { ProductTemplatePopup } from "@pos_manufacturing/js/ProductTemplatePopup";

patch(PosStore.prototype, {
    // @Override
    async _processData(loadedData) {
        await super._processData(...arguments);
        let self = this;
        this.db.product_template_by_id = {};
		this.db.product_tmpl_id = [];
		this.db.modifier_attribute_by_id = {};
		self._loadProductTemplate(loadedData['product.template']);
		self._loadModifierAttribute(loadedData['modifier.attribute']);
    },

    async addProductToCurrentOrder(product, options = {}) {
    	var self = this;
		if(self.config.product_configure){
            if (product.product_variant_count > 1) {
                var prod_template = this.db.product_template_by_id[product.product_tmpl_id];
                var prod_list = [];
                prod_template.product_variant_ids.forEach(function (prod) {
                    prod_list.push(self.db.get_product_by_id(prod));
                });
                this.env.services.pos.popup.add(ProductTemplatePopup, {'variant_ids':prod_list,'product':product});
            } else {
                if(product.to_weight && this.config.iface_electronic_scale){
                    this.showScreen('scale',{product: product});
                }else{
                    this.get_order().add_product
                }
                super.addProductToCurrentOrder(product, options = {})
            }
		}else{
		    super.addProductToCurrentOrder(product, options = {})
		}


        
    },


    _loadProductTemplate(product_templates) {
		var self = this;
		self.product_templates = product_templates;
		self.db.add_product_templates(product_templates);
	},

	_loadModifierAttribute(modifier_attribute){
		var self = this;
		self.side_prod_list = []
		self.modifier_attribute = modifier_attribute;
		self.modifier_prod = []
        self.db.add_product_modifier(modifier_attribute);
	},
    
});

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
       
    },

    set_modifier_attribute_list(modifier_attribute_list){
		this.modifier_attribute_list = modifier_attribute_list 
	},

	get_modifier_attribute_list(){
		return this.modifier_attribute_list;
	},

	export_as_JSON(){
		const json = super.export_as_JSON(...arguments);
		json.modifier_attribute_list = this.modifier_attribute_list || false;
        return json;
	},

	init_from_JSON(json){
		super.init_from_JSON(...arguments);
		this.modifier_attribute_list = json.modifier_attribute_list;
	}

});

patch(Orderline.prototype, {
    setup() {
        super.setup(...arguments);
        this.is_modifier = this.is_modifier || "";
        this.is_laterlity = this.is_laterlity;
       
    },

    getDisplayData() {
        return {
            ...super.getDisplayData(),
            line_modifier: this.get_modifier(),
        };
    },

    set_modifier(is_modifier){
		this.is_modifier = is_modifier;
        if (this.is_modifier){
            this.set_modifier_price(this.product.lst_price);
        }
	},

	set_unit_price(price){
		this.order.assert_editable();
        if(this.product.device_laterality)
        {
            this.is_laterlity = true;
            var total = price;   
            this.price = round_di(parseFloat(total) || 0, this.pos.dp['Product Price']);
        }
        else{
            this.price = round_di(parseFloat(price) || 0, this.pos.dp['Product Price']);
        }

	},

	set_modifier_price(price){
		var prods = this.get_modifier()
        var total = price;
        prods.forEach(function (prod) {
            if(prod)
            {
                
                if(prod.side_type == "bilateral"){
                    total += (prod.lst_price * prod.qty) 
                }

                if(prod.side_type == "left"){
                    var value = (prod.lst_price/2) * prod.qty 
                    total += value;
                }

                if(prod.side_type == "right"){
                    var value = (prod.lst_price/2) * prod.qty 
                    total += value;
                }
                
                if(prod.is_sub){
                    total += (prod.lst_price * prod.qty)
                }
            }   
        });
        this.set_unit_price(total);
	},

	get_modifier(){
		if(this.product.device_laterality)
        {
            this.is_laterlity = true;
        }
        return this.is_modifier
	},

	export_for_printing(){
		const json = super.export_for_printing(...arguments);
		json.is_modifier = this.get_modifier();
        return json;
	},

	export_as_JSON(){
		const json = super.export_as_JSON(...arguments);
		json.is_modifier = this.get_modifier() || false;
        json.is_laterlity = this.is_laterlity || false;
        return json;
	},
    
	init_from_JSON(json){
		super.init_from_JSON(...arguments);
		this.is_modifier = json.is_modifier;
        this.is_laterlity = json.is_laterlity;
	},

});    


	
