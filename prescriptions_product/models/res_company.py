# -*- coding: utf-8 -*-


from odoo import api, fields, models, api, _


class ResCompany(models.Model):
    _inherit = "res.company"

    prescriptions_product_settings = fields.Boolean()
    product_folder = fields.Many2one('prescriptions.folder', string="Product Workspace", check_company=True,
                                     default=lambda self: self.env.ref('prescriptions_product_folder',
                                                                       raise_if_not_found=False))
    product_tags = fields.Many2many('prescriptions.tag', 'product_tags_table')
