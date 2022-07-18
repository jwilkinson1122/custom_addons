odoo.define('pod_pos.ModifierProductPopup', function(require) {
	'use strict';

	const { useExternalListener } = owl.hooks;
	const PosComponent = require('point_of_sale.PosComponent');
	const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
	const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');
    const { useState } = owl.hooks;
    var rpc = require('web.rpc');

	class ModifierProductPopup extends AbstractAwaitablePopup {
		constructor() {
			super(...arguments);			
		}
		back(){
  			this.trigger('close-popup');
		}

		click_on_modifier_product(event){
        	// var product = this.options.selected_product
            var self = this;
            var order = this.env.pos.get_order();
        	var product_id = (event.currentTarget.dataset['productId']);
        	var product = self.env.pos.db.get_product_by_id(product_id)
        	var selectedLine = order.get_selected_orderline()
        	var vals_list = {};
        	var modifier_list = self.props.modifier_attribute
        	if(product){
	        	vals_list.id = product.id;
	        	vals_list.qty = 1;
	        	vals_list.display_name = product.display_name;
	        	vals_list.categ_id = product.categ_id;
	        	vals_list.image_url = product.image_url;
	        	vals_list.lst_price = product.lst_price;
	        	vals_list.name = product.name;
	        	vals_list.pos_categ_id = product.pos_categ_id;
	        	vals_list.product_template_attribute_value_ids = product.product_template_attribute_value_ids;
	        	vals_list.product_tmpl_id = product.product_tmpl_id;
	        	vals_list.taxes_id = product.taxes_id;
	        	vals_list.template_name = product.template_name;
	        	vals_list.uom_id = product.uom_id;
	        	vals_list.portion = self.props.portion;
	        	vals_list.portion_type = self.props.portion_type;
        	}
        	if (modifier_list.length > 0){
    			if (_.findWhere(modifier_list, {id: vals_list.id,})){
    				var increse = _.findWhere(modifier_list, {id:vals_list.id , portion: vals_list.portion})
    				if (increse && increse.portion == vals_list.portion){
    					increse.qty += 1; 
    				}
    				else{
    					modifier_list.push(vals_list)
    				}
    			}
    			else{
    				modifier_list.push(vals_list)
    			}
        	}
        	else{
        		modifier_list.push(vals_list)	
        	}
        	selectedLine.set_modifier(modifier_list);
        }
	}
	
	ModifierProductPopup.template = 'ModifierProductPopup';
	Registries.Component.add(ModifierProductPopup);
	return ModifierProductPopup;
});