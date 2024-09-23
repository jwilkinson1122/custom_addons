from odoo import models, fields, api

class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_pod_enable_options= fields.Boolean(
        related="pos_config_id.pod_enable_options", readonly=False)
    pos_pod_add_options_on_click_product= fields.Boolean(
        related="pos_config_id.pod_add_options_on_click_product", readonly=False)
    pos_pod_allow_same_product_different_qty= fields.Boolean(
        related="pos_config_id.pod_allow_same_product_different_qty", readonly=False)
        