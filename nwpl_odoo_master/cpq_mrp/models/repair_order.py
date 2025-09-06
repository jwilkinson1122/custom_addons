# -*- coding: utf-8 -*-
from odoo import fields, models


class RepairOrder(models.Model):
    _inherit = "repair.order"

    mrp_ids = fields.One2many("mrp.production", "repair_id", "Manufacting Orders")

    def action_view_repair_manufacturing_order(self):
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mrp.production",
            "res_id": self.mrp_ids.id,
        }
