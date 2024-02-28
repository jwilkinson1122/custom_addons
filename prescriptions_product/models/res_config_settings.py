# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    prescriptions_product_settings = fields.Boolean(related='company_id.prescriptions_product_settings', readonly=False,
                                                string="Product")
    product_folder = fields.Many2one('prescriptions.folder', related='company_id.product_folder', readonly=False,
                                     string="product default workspace")
    product_tags = fields.Many2many('prescriptions.tag', 'product_tags_table',
                                    related='company_id.product_tags', readonly=False,
                                    string="Product Tags")

    @api.onchange('product_folder')
    def on_product_folder_change(self):
        if self.product_folder != self.product_tags.mapped('folder_id'):
            self.product_tags = False
