/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class ModifierProductPopup extends AbstractAwaitablePopup {
    static template = "bi_pos_modify_own_pizza.ModifierProductPopup";

    setup() {
		super.setup();
		this.pos = usePos();
	}
	back(){
		this.cancel();
	}
	click_on_modifier_product(event){
    	// var product = this.options.selected_product
        var self = this;
        var order = this.pos.get_order();
    	var product_id = (event.currentTarget.dataset['productId']);
    	var product = self.pos.db.get_product_by_id(product_id)
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
    	if (modifier_list){
			if (modifier_list.length > 0){
	    		if (modifier_list.find((mod) => mod.id === vals_list.id && mod.portion === vals_list.portion)){
					var increse = modifier_list.find((mod) => mod.id === vals_list.id && mod.portion === vals_list.portion);
		    		if (increse && increse.portion == vals_list.portion){
		    			increse.qty += 1; 
		    		}else{
		    			modifier_list.push(vals_list)
		    		}
	    		}else{
					modifier_list.push(vals_list)
	    		}
	    	}
	    	else{
	    		modifier_list.push(vals_list)	
	    	}
	    	selectedLine.set_modifier(modifier_list);
    	}
    	
    }

   
}