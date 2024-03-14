from odoo import models, fields


class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pod_pos_enable_product_variants = fields.Boolean(
        related="pos_config_id.pod_pos_enable_product_variants", readonly=False)
    pod_pos_close_popup_after_single_selection = fields.Boolean(
        related="pos_config_id.pod_close_popup_after_single_selection", readonly=False)
    pod_pos_display_alternative_products = fields.Boolean(
        related="pos_config_id.pod_pos_display_alternative_products", readonly=False)
    pod_pos_variants_group_by_attribute = fields.Boolean(
        related="pos_config_id.pod_pos_variants_group_by_attribute", readonly=False)
