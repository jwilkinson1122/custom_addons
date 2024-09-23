# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_enable_prescriptions = fields.Boolean(related="pos_config_id.enable_prescriptions", readonly=False)
    group_prescription_disable_adding_lines = fields.Boolean(
        string="Disable adding more lines to SOs",
        implied_group="nwpl_pod_master.prescription_orders_disable_adding_lines",
    )