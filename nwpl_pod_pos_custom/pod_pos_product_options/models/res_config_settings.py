from odoo import models, fields, api

class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pod_pos_enable_options= fields.Boolean(
        related="pos_config_id.pod_enable_options", readonly=False)
    pod_pos_add_options_on_click_product= fields.Boolean(
        related="pos_config_id.pod_add_options_on_click_product", readonly=False)
    pod_pos_allow_same_product_different_qty= fields.Boolean(
        related="pos_config_id.pod_allow_same_product_different_qty", readonly=False)
        