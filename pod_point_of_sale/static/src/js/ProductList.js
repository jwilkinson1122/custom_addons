/** @odoo-module */

import { ProductsWidget } from "@point_of_sale/app/screens/product_screen/product_list/product_list";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ModifierProductPopup } from "@pod_point_of_sale/js/ModifierProductPopup";
import {ErrorPopup} from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";

patch(ProductsWidget.prototype,{

    setup() {
        super.setup();
        this.pos = usePos();
    },
    closeModifierScreen(){
		var self = this;
		$('.modifiers-list').hide();
        
        $('.product-list').show();
        $('.products-widget-control').show();
        $('.products-widget-control').removeClass('d-none');
		$('.product-list').removeClass('d-none');
    	self.modifier_attribute = [];
    	
        var DeviceRadio = document.querySelector(
			'input[type=radio][name=x]:checked'
		);
		if (DeviceRadio){
			DeviceRadio.checked = false;
			$('.modifiers-product-list').hide();
			$('#bilateral_device').hide();
    		$('#left_device').hide();
    		$('#right_device').hide();
    		$('#ask').show();
		}
	},

	doneModifier(){
    	$('.modifiers-list').hide();
    	$('.side-prod-list').show();
	},
	
	bilateral(){
        var self = this;
        $('#bilateral_device').show();
		$('#left_device').hide();
		$('#right_device').hide();
		$('#ask').hide();
		$('#left_side_device').hide();
		$('#right_side_device').hide();
		$('.modifiers-product-list').show();
		self.modifier_attribute = [];
    },
    left_side(){
    	var self = this;
    	$('#ask').hide();
    	$('#left_device').show();
    	$('#left_side_device').show();
		$('.modifiers-product-list').show();
    	$('#right_device').hide();
    	$('#bilateral_device').hide();
    	$('#right_side_device').hide();
    	self.modifier_attribute = [];
    	var inLeftRadio = document.querySelector(
			'input[name="left"]:checked'
		);
		if (inLeftRadio){
			$('.modifiers-product-list').show();	
		}
    },
    right_side(){
    	var self = this;
    	$('#ask').hide();
    	$('#right_device').show();
    	$('#right_side_device').show();
		$('.modifiers-product-list').show();
    	$('#left_device').hide();
    	$('#bilateral_device').hide();
    	$('#left_side_device').hide();
    	self.modifier_attribute = [];
    	var inRightRadio = document.querySelector(
			'input[name="right"]:checked'
		);
		if (inRightRadio){
			$('.modifiers-product-list').show();	
		}
    },

    modifierSelection(event){
    	var self = this;
    	var modifier_prod_list = [] 
    	var selected_modifier_id = parseInt(event.currentTarget.dataset['productId'])

    	var product = self.pos.db.get_product_by_id(selected_modifier_id)
    	
    	var checkRadio = document.querySelector(
			'input[name="x"]:checked'
		);
    	var side = false;
    	var side_type = false;
		if(checkRadio.value == "bilateral"){
			side = "Bilateral Device"
			side_type ="bilateral"
		}
		else if(checkRadio.value == "left"){
			var leftRadio = document.querySelector('input[name="left"]:checked');
			side_type ="left"
			if (leftRadio.value == "left side"){side = "Left Side"}
		}
		else if(checkRadio.value == "right"){
			var rightRadio = document.querySelector('input[name="right"]:checked');
			side_type ="right"
			if (rightRadio.value == "right side"){side = "Right Side"}
		}

    	product['image_url'] = `/web/image?model=product.product&field=image_128&id=${product.id}&write_date=${product.write_date}&unique=1`;
    	modifier_prod_list.push(product)
    	self.pos.popup.add(ModifierProductPopup,{
            modifier_prod: modifier_prod_list,
            side: side,
            side_type: side_type,
            modifier_attribute: self.modifier_attribute,
        })
    },

    selectSubProduct(){
    	var self = this;
    	var order = self.pos.get_order();
    	var product = order.get_selected_orderline().product;     
    	

    	if (self.pos.side_prod_list.length == 0 ){
    		self.pos.popup.add(ErrorPopup, {
				title: _t('Side Product'),
				body: _t('Side Products Are Not Define For This Product.'),
			});
    	}else{
    		$('.side-prod-info').show();
    		$('.side-prod-list').hide();
    		/*if($('.side-prod-info').hasClass('oe_hidden')){
    			$('.side-prod-info').removeClass('oe_hidden');
    		}*/
    	}
    },

    cancel_add_side_product(){
    	$('.side-prod-list').hide();

    	$('.products-widget-control').removeClass('d-none');
		$('.product-list').removeClass('d-none');
    	// $('.product-list').show();
        // $('.products-widget-control').show();
        var DeviceRadio = document.querySelector(
			'input[type=radio][name=x]:checked'
		);
		if (DeviceRadio){
			DeviceRadio.checked = false;
			$('.modifiers-product-list').hide();
			$('#bilateral_device').hide();
    		$('#left_device').hide();
    		$('#right_device').hide();
    		$('#ask').show();
		}
    },

    add_sub_product(event){
    	var self = this;
    	var product_id = (event.currentTarget.dataset['productId']);
		var product = self.pos.db.get_product_by_id(product_id);
    	var order = self.pos.get_order();
    	var selectedLine = order.get_selected_orderline();
    	

    	var vals_list = {};
    	var modifier_list = self.modifier_attribute;
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
        	vals_list.is_sub = true;
    	}
    	if (modifier_list){
    		if (modifier_list.length > 0){

	    		var increse = modifier_list.find((mod) => mod.id === vals_list.id);
	    		if (increse){

		    		increse.qty += 1; 
	    		}
	    		else{
					modifier_list.push(vals_list)
				}

				
				
	    	}
	    	else{
	    		modifier_list.push(vals_list)	
	    	}
	    	selectedLine.set_modifier(modifier_list)
    	}
    	
    },

    doneSubProduct(){
    	$('.side-prod-info').hide();
    	$('.products-widget-control').removeClass('d-none');
		$('.product-list').removeClass('d-none');
    	// $('.product-list').show();
        // $('.products-widget-control').show();
        var DeviceRadio = document.querySelector(
			'input[type=radio][name=x]:checked'
		);
		if (DeviceRadio){
			DeviceRadio.checked = false;
			$('.modifiers-product-list').hide();
			$('#bilateral_device').hide();
    		$('#left_device').hide();
    		$('#right_device').hide();
    		$('#ask').show();
		}
    }
    
});

