# -*- coding: utf-8 -*-

from odoo import models, _

import logging

_logger = logging.getLogger(__name__)

class POSSession(models.Model):
	_inherit = 'pos.session'

	def _loader_params_product_product(self):
		res = super(POSSession, self)._loader_params_product_product()
		fields = res.get('search_params').get('fields')
		fields.extend(['product_template_attribute_value_ids','modifier_attribute_product_id','device_laterality','sub_products_ids'])
		res['search_params']['fields'] = fields
		return res

	def _pos_ui_models_to_load(self):
		result = super()._pos_ui_models_to_load()
		result.extend(['product.template','modifier.attribute'])
		return result

	def _loader_params_product_template(self):
		return {
			'search_params': {
				'domain': [('sale_ok','=',True),('available_in_pos','=',True)],
				'fields': ['name','display_name','product_variant_ids','product_variant_count']
			}
		}

	def _get_pos_ui_product_template(self, params):
		return self.env['product.template'].search_read(**params['search_params'])



	def _loader_params_modifier_attribute(self):
		return {
			'search_params': {
				'domain': [], 
				'fields': ['name','product_id','price','uom_id','display_name']
			}
		}

	def _get_pos_ui_modifier_attribute(self, params):
		return self.env['modifier.attribute'].search_read(**params['search_params'])