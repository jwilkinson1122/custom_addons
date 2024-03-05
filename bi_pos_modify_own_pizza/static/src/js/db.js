/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosDB } from "@point_of_sale/app/store/db";

patch(PosDB.prototype, {
	init: function(options){
		this.product_template_by_id = {};
		this.product_tmpl_id = [];
		this.modifier_attribute_by_id = {};
		this._super(options);
	},
	add_product_templates: function(product_templates){
		for(var temp=0 ; temp < product_templates.length; temp++){
			var product_template_attribute_value_ids = [];
			var prod_temp =  product_templates[temp] ; 
			this.product_template_by_id[prod_temp.id] = prod_temp;
			this.product_tmpl_id.push(prod_temp)
			for (var prod = 0; prod <prod_temp.product_variant_ids.length; prod++){
				var product = this.product_by_id[prod_temp.product_variant_ids[prod]]



				if (product) {
					for (var i = 0; i < product.product_template_attribute_value_ids.length; i++){
						product_template_attribute_value_ids.push(product.product_template_attribute_value_ids[i]);
					}
					product.template_name = prod_temp.name
					product.product_variant_count = prod_temp.product_variant_count;
				}
			}
			const unique_attribute_value_ids = [...new Set(product_template_attribute_value_ids)]
			this.product_template_by_id[prod_temp.id].product_template_attribute_value_ids = unique_attribute_value_ids;
		}
	},

	add_product_modifier: function(modifier_attribute){
		for(var temp=0 ; temp < modifier_attribute.length; temp++){
			var product_template_attribute_value_ids = [];
			var prod_modi =  modifier_attribute[temp] ;
			this.modifier_attribute_by_id[prod_modi.id] = prod_modi;
		}
	},


    get_product_by_category: function(category_id){
        var product_ids  = this.product_by_category_id[category_id];
        var list = [];
        var temp = this.product_tmpl_id;
        // var prods = []
        var product_tmpl_lst = []
        if (product_ids) {
            for (var i = 0; i < temp.length; i++) {
                for (var j = 0 ; j < product_ids.length ; j++){
                    var prd_prod = this.product_by_id[product_ids[j]]
                    if(jQuery.inArray( prd_prod.product_tmpl_id, product_tmpl_lst ) == -1){
                        if(prd_prod.product_tmpl_id == temp[i].id){
                            var prd_list = temp[i].product_variant_ids.sort();
                            list.push(prd_prod)
                            product_tmpl_lst.push(temp[i].id)
                        }
                    }
                }
            }
        }
        return list;
    },
    search_product_in_category: function(category_id, query){
        try {
            query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
            query = query.replace(/ /g,'.+');
            var re = RegExp("([0-9]+):.*?"+utils.unaccent(query),"gi");
        }catch(e){
            return [];
        }
        var results = [];
        var product_tmpl_lst = []
        var temp = this.product_tmpl_id;
        for(var i = 0; i < this.limit; i++){
            var r = re.exec(this.category_search_string[category_id]);
            if(r){
                var id = Number(r[1]);
                var prod  = this.get_product_by_id(id)
                for(var j = 0; j < temp.length ; j++){
                    if(jQuery.inArray( prod.product_tmpl_id, product_tmpl_lst ) == -1){
                        if(prod.product_tmpl_id == temp[j].id){
                            var prd_list = temp[i].product_variant_ids.sort();
                            results.push(prod)
                            product_tmpl_lst.push(temp[j].id)
                        }
                    }
                }
            }else{
                break;
            }
        }
        return results;
    },
});