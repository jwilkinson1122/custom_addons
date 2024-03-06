# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    allow_decrease_kitchen = fields.Boolean(
        "Allow change Qty for kitchen orders", default=True
    )
    allow_remove_kitchen_order_line = fields.Boolean(
        "Allow remove kitchen order line", default=True
    )

    @api.onchange("allow_delete_order_line")
    def _onchange_allow_delete_order_line(self):
        if self.allow_delete_order_line is False:
            self.allow_remove_kitchen_order_line = False
