odoo.define("podiatry_pos_modifier.screens", function (require) {
	"use strict";

	var models = require('point_of_sale.models');
	var PosDB = require("point_of_sale.DB");

	var core = require('web.core');
	var utils = require('web.utils');

	var QWeb = core.qweb;
	var _t = core._t;
	var _super_posmodel = models.PosModel.prototype;
	models.PosModel = models.PosModel.extend({
		initialize: function (session, attributes) {
			var product_model = _.find(this.models, function (model) { return model.model === 'product.product'; });
			product_model.fields.push('product_template_attribute_value_ids');
			return _super_posmodel.initialize.call(this, session, attributes);
		},
	});

	models.load_models({
		model: 'product.template',
		fields: ['name', 'display_name', 'product_variant_ids', 'product_variant_count',],
		domain: [['sale_ok', '=', true], ['available_in_pos', '=', true]],
		loaded: function (self, product_templates) {
			self.product_templates = product_templates;
			self.db.add_product_templates(product_templates);
		},
	});

	models.load_models({
		model: 'modifier.attribute',
		fields: ['name', 'product_id', 'price', 'uom_id', 'display_name'],

		loaded: function (self, modifier_attribute) {
			self.side_prod_list = []
			self.modifier_attribute = modifier_attribute;
			self.modifier_prod = []
			self.db.add_product_modifier(modifier_attribute);
		},
	});

	models.load_fields('product.product', ['modifier_attribute_product_id', 'laterality_display', 'sub_products_ids']);

	PosDB.include({
		init: function (options) {
			this.product_template_by_id = {};
			this.product_tmpl_id = [];
			this.modifier_attribute_by_id = {};
			this._super(options);
		},
		add_product_templates: function (product_templates) {
			for (var temp = 0; temp < product_templates.length; temp++) {
				var product_template_attribute_value_ids = [];
				var prod_temp = product_templates[temp];
				this.product_template_by_id[prod_temp.id] = prod_temp;
				this.product_tmpl_id.push(prod_temp)
				for (var prod = 0; prod < prod_temp.product_variant_ids.length; prod++) {
					var product = this.product_by_id[prod_temp.product_variant_ids[prod]]
					for (var i = 0; i < product.product_template_attribute_value_ids.length; i++) {
						product_template_attribute_value_ids.push(product.product_template_attribute_value_ids[i]);
					}
					product.template_name = prod_temp.name
					product.product_variant_count = prod_temp.product_variant_count;
				}
				const unique_attribute_value_ids = [...new Set(product_template_attribute_value_ids)]
				this.product_template_by_id[prod_temp.id].product_template_attribute_value_ids = unique_attribute_value_ids;
			}
		},

		add_product_modifier: function (modifier_attribute) {
			for (var temp = 0; temp < modifier_attribute.length; temp++) {
				var product_template_attribute_value_ids = [];
				var prod_modi = modifier_attribute[temp];
				this.modifier_attribute_by_id[prod_modi.id] = prod_modi;
			}
		},


		get_product_by_category: function (category_id) {
			var product_ids = this.product_by_category_id[category_id];
			var list = [];
			var temp = this.product_tmpl_id;
			// var prods = []
			var product_tmpl_lst = []
			if (product_ids) {
				for (var i = 0; i < temp.length; i++) {
					for (var j = 0; j < product_ids.length; j++) {
						var prd_prod = this.product_by_id[product_ids[j]]
						if (jQuery.inArray(prd_prod.product_tmpl_id, product_tmpl_lst) == -1) {
							if (prd_prod.product_tmpl_id == temp[i].id) {
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
		/* returns a list of products with :
		 * - a category that is or is a child of category_id,
		 * - a name, package or barcode containing the query (case insensitive) 
		 */
		search_product_in_category: function (category_id, query) {
			try {
				query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g, '.');
				query = query.replace(/ /g, '.+');
				var re = RegExp("([0-9]+):.*?" + utils.unaccent(query), "gi");
			} catch (e) {
				return [];
			}
			var results = [];
			var product_tmpl_lst = []
			var temp = this.product_tmpl_id;
			for (var i = 0; i < this.limit; i++) {
				var r = re.exec(this.category_search_string[category_id]);
				if (r) {
					var id = Number(r[1]);
					var prod = this.get_product_by_id(id)
					for (var j = 0; j < temp.length; j++) {
						if (jQuery.inArray(prod.product_tmpl_id, product_tmpl_lst) == -1) {
							if (prod.product_tmpl_id == temp[j].id) {
								var prd_list = temp[i].product_variant_ids.sort();
								results.push(prod)
								product_tmpl_lst.push(temp[j].id)
							}
						}
					}
				} else {
					break;
				}
			}
			return results;
		},
	});
});
