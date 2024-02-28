# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


class Prescription(models.Model):
    _inherit = 'prescriptions.prescription'

    product_template_id = fields.Many2one('product.template', string="Product", compute='_compute_product', search='_search_product_template_id')
    product_id = fields.Many2one('product.product', string="Product Variant", compute='_compute_product', search='_search_product_id')

    @api.depends('res_id', 'res_model')
    def _compute_product(self):
        ProductTemplate = self.env['product.template']
        Product = self.env['product.product']
        for prescription in self:
            prescription.product_template_id = prescription.res_model == 'product.template' and ProductTemplate.browse(prescription.res_id)
            prescription.product_id = prescription.res_model == 'product.product' and Product.browse(prescription.res_id)

    @api.model
    def _search_product_template_id(self, operator, value):
        return self._search_related_product_field(operator, value, self.env['product.template'])

    @api.model
    def _search_product_id(self, operator, value):
        return self._search_related_product_field(operator, value, self.env['product.product'])

    @api.model
    def _search_related_product_field(self, operator, value, Model):
        if operator in ('=', '!=') and isinstance(value, bool):
            if not value:
                operator = expression.TERM_OPERATORS_NEGATION[operator]
            return [("res_model", operator, Model._name)]
        elif operator in ('=', '!=', "in", "not in") and isinstance(value, (int, list)):
            return expression.AND([[("res_model", "=", Model._name)], [("res_id", operator, value)]])
        elif operator in ("ilike", "not ilike", "=", "!=") and isinstance(value, str):
            query_model = Model._search([(Model._rec_name, operator, value)])
            query_doc = self._search([('res_model', '=', Model._name), ('res_id', 'in', query_model)])
            return [("id", "in", query_doc)]
        raise ValidationError(_("Invalid %s search", self.env['ir.model']._get(Model._name).name))
