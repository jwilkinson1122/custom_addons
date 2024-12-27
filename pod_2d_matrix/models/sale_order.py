from datetime import date, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    laterality_matrix = fields.One2many(
        "podiatry.laterality.matrix",
        "order_id",
        string="Laterality Matrix",
    )

    # Button to open the wizard
    def open_laterality_wizard(self):
        return {
            "name": "Select Products by Laterality",
            "type": "ir.actions.act_window",
            "res_model": "podiatry.laterality.wizard",
            "view_mode": "form",
            "view_id": self.env.ref("podiatry.view_podiatry_laterality_wizard_form").id,
            "target": "new",
        }
