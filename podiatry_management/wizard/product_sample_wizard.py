# -*- coding: utf-8 -*-

from odoo import api, fields, models


class product_sample_wizard(models.TransientModel):
    """
    The wizard to be inherited in any update wizard which assume writing mass values in templates
    """
    _name = "product.sample.wizard"
    _description = "Product Update"

    products = fields.Char(string="Updated products",)

    @api.model
    def create(self, values):
        """
        Overwrite to trigger products update

        Methods:
         * action_update_products

        Extra info:
         *  we do not use standard wizard buttons in the footer to use standard js forms
        """
        res = super(product_sample_wizard, self).create(values)
        res.action_update_products()
        return res

    def action_update_products(self):
        """
        The method to update products in batch

        Methods:
         * _update_products

        Extra info:
         * we use products char instead of m2m as ugly hack to avoid default m2m strange behaviour
         * Expected singleton
        """
        self.ensure_one()
        product_ids = self.products.split(",")
        product_ids = [int(pr) for pr in product_ids]
        product_ids = self.env["product.template"].browse(product_ids)
        if product_ids:
            self._update_products(product_ids)

    def _update_products(self, product_ids):
        """
        Dummy method to prepare values
        It is to be inherited in a real update wizard

        Args:
         * product_ids - product.template recordset
        """
        pass
