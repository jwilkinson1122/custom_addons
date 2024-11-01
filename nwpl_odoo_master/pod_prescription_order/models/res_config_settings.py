# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    group_prescription_disable_adding_lines = fields.Boolean(
        string="Disable adding more lines to SOs",
        implied_group="nwpl_odoo_master.prescription_orders_disable_adding_lines",
    )
