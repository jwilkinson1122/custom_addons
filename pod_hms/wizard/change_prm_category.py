# -*- coding: utf-8 -*-

from odoo import api, fields, models

class change_prm_category(models.TransientModel):
    _name = "change.prm.category"
    _inherit = "product.sample.wizard"
    _description = "Update Category"

    category_id = fields.Many2one(
        "product.category",
        string="New category",
        required=True,
    )

    def _update_products(self, product_ids):
        """
        The method to prepare new vals for category

        Args:
         * product_ids - product.template recordset

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        product_ids.write({"categ_id": self.category_id.id})
