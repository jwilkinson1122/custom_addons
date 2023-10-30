# -*- coding: utf-8 -*-


import base64

from odoo import api, fields, models

from odoo.modules.module import get_module_resource


class PrescriptionProductCategory(models.Model):
    _name = 'prescription.product.category'
    _inherit = 'image.mixin'
    _description = 'Prescription Product Category'

    @api.model
    def _default_image(self):
        image_path = get_module_resource('prescription', 'static/img', 'insole_circle_green.png')
        return base64.b64encode(open(image_path, 'rb').read())

    name = fields.Char('Product Category', required=True, translate=True)
    company_id = fields.Many2one('res.company')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    product_count = fields.Integer(compute='_compute_product_count', help="The number of products related to this category")
    active = fields.Boolean(string='Active', default=True)
    image_1920 = fields.Image(default=_default_image)

    def _compute_product_count(self):
        product_data = self.env['prescription.product'].read_group([('category_id', 'in', self.ids)], ['category_id'], ['category_id'])
        data = {product['category_id'][0]: product['category_id_count'] for product in product_data}
        for category in self:
            category.product_count = data.get(category.id, 0)

    def toggle_active(self):
        """ Archiving related prescription product """
        res = super().toggle_active()
        Product = self.env['prescription.product'].with_context(active_test=False)
        all_products = Product.search([('category_id', 'in', self.ids)])
        all_products._sync_active_from_related()
        return res