

from odoo import models, fields


class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pod_pos_remove_all_item = fields.Boolean(related="pos_config_id.pod_remove_all_item", readonly=False)
    pod_validation_to_remove_all_item  = fields.Boolean(related="pos_config_id.pod_validation_to_remove_all_item",readonly=False)
    pod_validation_to_remove_single_item = fields.Boolean(related="pos_config_id.pod_validation_to_remove_single_item", readonly=False)
    