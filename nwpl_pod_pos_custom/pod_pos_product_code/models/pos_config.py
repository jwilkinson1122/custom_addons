

from odoo import models, fields


class PosConfig(models.Model):
    _inherit = "pos.config"

    pod_enable_prduct_code = fields.Boolean("Enable Product Internal Ref")
    pod_enable_product_code_in_cart = fields.Boolean(string="Enable Internal Reference in Cart")
    pod_enable_product_code_in_receipt = fields.Boolean(string="Enable Internal Reference in Receipt")
