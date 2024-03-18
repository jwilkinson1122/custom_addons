

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_pod_enable_prduct_code = fields.Boolean(
        related="pos_config_id.pod_enable_prduct_code", readonly=False
    )
    pos_pod_enable_product_code_in_cart = fields.Boolean(
        related="pos_config_id.pod_enable_product_code_in_cart", readonly=False
    )
    pos_pod_enable_product_code_in_receipt = fields.Boolean(
        related="pos_config_id.pod_enable_product_code_in_receipt", readonly=False
    )
