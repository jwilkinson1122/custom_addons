

from odoo import fields, models


class PlanDefinitionAction(models.Model):
    _inherit = "workflow.plan.definition.action"

    variable_fee = fields.Float(string="Variable fee (%)", default="0.0")
    fixed_fee = fields.Float(string="Fixed fee", default="0.0")
    pod_commission = fields.Boolean(
        related="activity_definition_id.service_id.pod_commission",
        readonly=True,
    )
