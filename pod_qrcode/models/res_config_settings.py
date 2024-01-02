# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """Extends the res.config.settings model to include configuration
    settings for QR code prefixes."""
    _inherit = 'res.config.settings'

    customer_prefix = fields.Char(string="Customer QR Prefix",
                                  help='Customer Qr prefix')
    product_prefix = fields.Char(string="Product QR Prefix",
                                 help='Product Qr prefix')

    def get_values(self):
        """fRetrieve the current configuration values for QR code prefixes."""
        res = super().get_values()
        customer_prefix = self.env["ir.config_parameter"].get_param(
            "customer_product_qr.config.customer_prefix")
        product_prefix = self.env["ir.config_parameter"].get_param(
            "customer_product_qr.config.product_prefix")
        res.update({
            'customer_prefix': customer_prefix if type(
                customer_prefix) else False,
            'product_prefix': product_prefix if type(product_prefix) else False
        }
        )
        return res

    def set_values(self):
        """Set the configuration values for QR code prefixes."""
        self.env['ir.config_parameter'].sudo().set_param(
            'customer_product_qr.config.customer_prefix', self.customer_prefix)
        self.env['ir.config_parameter'].sudo().set_param(
            'customer_product_qr.config.product_prefix', self.product_prefix)
        super().set_values()
