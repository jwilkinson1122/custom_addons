# -*- coding: utf-8 -*-

from odoo import api, fields, models

class update_prm_price(models.TransientModel):
    _name = "update.prm.price"
    _inherit = "product.sample.wizard"
    _description = "Update Sales Price"

    price = fields.Float("Sales Price", required=True)

    def _update_products(self, product_ids):
        """
        The method to prepare new vals for price

        Args:
         * product_ids - product.template recordset

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        product_ids.write({"list_price": self.price})
