from odoo import fields, models


class PodiatryCareplanAddPlanDefinition(models.TransientModel):
    _inherit = "pod.careplan.add.plan.definition"

    order_by_id = fields.Many2one("res.partner", domain=[("is_requester", "=", True)])

    def _get_values(self):
        values = super(PodiatryCareplanAddPlanDefinition, self)._get_values()
        values["order_by_id"] = self.order_by_id.id or False
        return values
