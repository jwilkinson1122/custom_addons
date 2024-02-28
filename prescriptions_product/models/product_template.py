# -*- coding: utf-8 -*-


from odoo import models


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'prescriptions.mixin']

    def _get_prescription_tags(self):
        company = self.company_id or self.env.company
        return company.product_tags

    def _get_prescription_folder(self):
        company = self.company_id or self.env.company
        return company.product_folder

    def _check_create_prescriptions(self):
        company = self.company_id or self.env.company
        return company.prescriptions_product_settings and super()._check_create_prescriptions()
