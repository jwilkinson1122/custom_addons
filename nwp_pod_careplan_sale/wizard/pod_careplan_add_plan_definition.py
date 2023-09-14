

from odoo import fields, models


class PodiatryCareplanAddPlanDefinition(models.TransientModel):
    _inherit = "pod.careplan.add.plan.definition"

    qty = fields.Integer(default=1)
    order_by_id = fields.Many2one("res.partner")

    def _get_values(self):
        values = super()._get_values()
        values["sub_payor_id"] = self.careplan_id.sub_payor_id.id
        values["invoice_group_method_id"] = (
            self.authorization_method_id.invoice_group_method_id.id or False
        )
        values["qty"] = self.qty
        return values
