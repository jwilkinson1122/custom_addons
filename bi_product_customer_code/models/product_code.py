import re
import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ProductProductCode(models.Model):

	_name = "product.product.code"
	_description = " Product Code"

	code = fields.Char("Code")


class ProductProduct(models.Model):

	_inherit = "product.product"


	@api.model
	def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None, order=None):
		if not args:
			args = []
		if name:
			positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
			product_ids = []	
			if not product_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
				
				product_ids = list(self._search(args + [('name', operator, name)], limit=limit))
			if not product_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
				
				product_ids = list(self._search(args + [('default_code', operator, name)], limit=limit))
			if not product_ids and self._context.get('partner_id'):
				suppliers_ids = self.env['product.customer.code']._search([
					('name_id', '=', self._context.get('partner_id')),
					'|',
					('product_code', operator, name),
					('product_name', operator, name)], access_rights_uid=name_get_uid)
				if suppliers_ids:
					product_ids = self._search([('product_tmpl_id.product_customer_code_ids', 'in', suppliers_ids)], limit=limit, access_rights_uid=name_get_uid)
		else:
			product_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
		return product_ids

	