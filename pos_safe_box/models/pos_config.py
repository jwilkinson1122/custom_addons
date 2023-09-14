from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    safe_box_group_id = fields.Many2one("safe.box.group", string="Safe box system")
