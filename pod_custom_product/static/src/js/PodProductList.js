// PodProductList js
odoo.define('pod_custom_product.PodProductList', function(require) {
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

	const PodProductList = (ProductList) =>
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
            	
                var DeviceRadio = document.querySelector( 'input[type=radio][name=x]:checked'
				);
				if (DeviceRadio){
					DeviceRadio.checked = false;
					$('.modifiers-product-list').hide();
					$('#single_device').hide();
		    		$('#bilateral_device').hide();
		    		$('#ask').show();
				}
			}

			doneModifier(){
				// self.side_prod_list = []
            	$('.modifiers-list').hide();
            	$('.side-prod-list').show();
			}
			
			single_side(){
	            var self = this;
	            $('#single_device').show();
	    		$('#bilateral_device').hide();
	    		$('#ask').hide();
	    		$('#bilateral_side_device').hide();
	    		$('.modifiers-product-list').show();
	    		self.modifier_attribute = [];
	        }
	        bilateral_side(){
	        	var self = this;
	        	$('#ask').hide();
	        	$('#bilateral_device').show();
	        	$('#bilateral_side_device').show();
	    		$('.modifiers-product-list').show();
	        	$('#single_device').hide();
	        	self.modifier_attribute = [];
	        	var sideRadio = document.querySelector( 'input[name="bilateral"]:checked'
				);
        		if (sideRadio){
        			$('.modifiers-product-list').show();	
        		}
	        }

	        modifierSelection(event){
	        	var self = this;
	        	var modifier_prod_list = [] 
            	var selected_modifier_id = parseInt(event.currentTarget.dataset['productId'])

            	var product = self.env.pos.db.get_product_by_id(selected_modifier_id)
            	
            	var checkRadio = document.querySelector( 'input[name="x"]:checked'
				);
            	var side = false;
            	var side_type = false;
				if(checkRadio.value == "single"){
					side = "Single Device"
					side_type ="single"
				}else if(checkRadio.value == "bilateral"){
					var bilateralRadio = document.querySelector( 'input[name="bilateral"]:checked'
					);
					side_type ="bilateral"
					if (bilateralRadio.value == "left side"){
						side = "Left Side";
					}else if(bilateralRadio.value == "right side"){
						side = "Right Side";
					}
				}
		
            	product['image_url'] = `/web/image?model=product.product&field=image_128&id=${product.id}&write_date=${product.write_date}&unique=1`;
            	modifier_prod_list.push(product)
            	self.showPopup('ModifierProductPopup',{
                    modifier_prod: modifier_prod_list,
                    side: side,
                    side_type: side_type,
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
                var DeviceRadio = document.querySelector( 'input[type=radio][name=x]:checked'
				);
				if (DeviceRadio){
					DeviceRadio.checked = false;
					$('.modifiers-product-list').hide();
					$('#single_device').hide();
		    		$('#bilateral_device').hide();
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
                var DeviceRadio = document.querySelector( 'input[type=radio][name=x]:checked'
				);
				if (DeviceRadio){
					DeviceRadio.checked = false;
					$('.modifiers-product-list').hide();
					$('#single_device').hide();
		    		$('#bilateral_device').hide();
		    		$('#ask').show();
				}
	        }
		};

	Registries.Component.extend(ProductList, PodProductList);

	return ProductList;

});
