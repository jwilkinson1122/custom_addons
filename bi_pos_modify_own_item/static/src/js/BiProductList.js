
// BiProductList js
odoo.define('bi_pos_modify_own_pizza.BiProductList', function(require) {
	"use strict";

	const models = require('point_of_sale.models');
	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const Session = require('web.Session');
	const chrome = require('point_of_sale.Chrome');
	const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
	const NumberBuffer = require('point_of_sale.NumberBuffer');
	const { useListener } = require('web.custom_hooks');
	const { onChangeOrder, useBarcodeReader } = require('point_of_sale.custom_hooks');
	const { useState } = owl.hooks;

	const ProductList = require('point_of_sale.ProductList'); 

	const BiProductList = (ProductList) =>
		class extends ProductList {
			constructor() {
				super(...arguments);
				// this.side_prod_list = []
				
			}
			closeModifierScreen(){
				var self = this;
				$('.modifiers-list').hide();
	            
	            $('.product-list').show();
                $('.products-widget-control').show();
            	self.modifier_attribute = [];
            	
                var PizzaRadio = document.querySelector(
					'input[type=radio][name=x]:checked'
				);
				if (PizzaRadio){
					PizzaRadio.checked = false;
					$('.modifiers-product-list').hide();
					$('#full_pizza').hide();
		    		$('#half_pizza').hide();
		    		$('#quater_pizza').hide();
		    		$('#ask').show();
				}
			}

			doneModifier(){
				// self.side_prod_list = []
            	$('.modifiers-list').hide();
            	$('.side-prod-list').show();
			}
			
			full_size(){
	            var self = this;
	            $('#full_pizza').show();
	    		$('#half_pizza').hide();
	    		$('#quater_pizza').hide();
	    		$('#ask').hide();
	    		$('#half_size_pizza').hide();
	    		$('#quater_size_pizza').hide();
	    		$('.modifiers-product-list').show();
	    		self.modifier_attribute = [];
	        }
	        half_size(){
	        	var self = this;
	        	$('#ask').hide();
	        	$('#half_pizza').show();
	        	$('#half_size_pizza').show();
	    		$('.modifiers-product-list').show();
	        	$('#quater_pizza').hide();
	        	$('#full_pizza').hide();
	        	$('#quater_size_pizza').hide();
	        	self.modifier_attribute = [];
	        	var inHalfRadio = document.querySelector(
					'input[name="half"]:checked'
				);
        		if (inHalfRadio){
        			$('.modifiers-product-list').show();	
        		}
	        }
	        quater_size(){
	        	var self = this;
	        	$('#ask').hide();
	        	$('#quater_pizza').show();
	        	$('#quater_size_pizza').show();
	    		$('.modifiers-product-list').show();
	        	$('#half_pizza').hide();
	        	$('#full_pizza').hide();
	        	$('#half_size_pizza').hide();
	        	self.modifier_attribute = [];
	        	var inQuaterRadio = document.querySelector(
					'input[name="quater"]:checked'
				);
        		if (inQuaterRadio){
        			$('.modifiers-product-list').show();	
        		}
	        }

	        modifierSelection(event){
	        	var self = this;
	        	var modifier_prod_list = [] 
            	var selected_modifier_id = parseInt(event.currentTarget.dataset['productId'])

            	var product = self.env.pos.db.get_product_by_id(selected_modifier_id)
            	
            	var checkRadio = document.querySelector(
					'input[name="x"]:checked'
				);
            	var portion = false;
            	var portion_type = false;
				if(checkRadio.value == "full"){
					portion = "Full Pizza"
					portion_type ="full"
				}else if(checkRadio.value == "half"){
					var halfRadio = document.querySelector(
						'input[name="half"]:checked'
					);
					portion_type ="half"
					if (halfRadio.value == "left half"){
						portion = "Left Half";
					}else if(halfRadio.value == "right half"){
						portion = "Right Half";
					}
				}else if(checkRadio.value == "quater"){
					var quaterRadio = document.querySelector(
						'input[name="quater"]:checked'
					);
					portion_type ="quater"
					if (quaterRadio.value == "1st quater"){
						portion = "1st quater";
					}else if(quaterRadio.value == "2nd quater"){
						portion = "2nd quater";
					}else if(quaterRadio.value == "3rd quater"){
						portion = "3rd quater";
					}else if(quaterRadio.value == "4th quater"){
						portion = "4th quater";
					}
				}

            	product['image_url'] = `/web/image?model=product.product&field=image_128&id=${product.id}&write_date=${product.write_date}&unique=1`;
            	modifier_prod_list.push(product)
            	self.showPopup('ModifierProductPopup',{
                    modifier_prod: modifier_prod_list,
                    portion: portion,
                    portion_type: portion_type,
                    modifier_attribute: self.modifier_attribute,
                })
	        }

	        selectSubProduct(){
	        	var self = this;
	        	var order = self.env.pos.get_order();
	        	var product = order.get_selected_orderline().product;     
            	

            	if (self.env.pos.side_prod_list.length == 0 ){
            		self.showPopup('ErrorPopup', {
						title: self.env._t('Side Product'),
						body: self.env._t('Side Products Are Not Define For This Product.'),
					});
            	}else{
            		$('.side-prod-info').show();
            		$('.side-prod-list').hide();
            	}
	        }

	        cancel_add_side_product(){
            	$('.side-prod-list').hide();
	        	$('.product-list').show();
                $('.products-widget-control').show();
                var PizzaRadio = document.querySelector(
					'input[type=radio][name=x]:checked'
				);
				if (PizzaRadio){
					PizzaRadio.checked = false;
					$('.modifiers-product-list').hide();
					$('#full_pizza').hide();
		    		$('#half_pizza').hide();
		    		$('#quater_pizza').hide();
		    		$('#ask').show();
				}
	        }

	        add_sub_product(event){
	        	var self = this;
	        	var product_id = (event.currentTarget.dataset['productId']);
				var product = self.env.pos.db.get_product_by_id(product_id);
            	var order = self.env.pos.get_order();
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
	        	if (modifier_list.length > 0){
	    			if (_.findWhere(modifier_list, {id: vals_list.id})){
	    				var increse = _.findWhere(modifier_list, {id: vals_list.id})
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

	        doneSubProduct(){
	        	$('.side-prod-info').hide();
	        	$('.product-list').show();
                $('.products-widget-control').show();
                var PizzaRadio = document.querySelector(
					'input[type=radio][name=x]:checked'
				);
				if (PizzaRadio){
					PizzaRadio.checked = false;
					$('.modifiers-product-list').hide();
					$('#full_pizza').hide();
		    		$('#half_pizza').hide();
		    		$('#quater_pizza').hide();
		    		$('#ask').show();
				}
	        }
		};

	Registries.Component.extend(ProductList, BiProductList);

	return ProductList;

});
