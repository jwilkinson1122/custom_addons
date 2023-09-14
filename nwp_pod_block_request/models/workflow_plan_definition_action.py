

from odoo import fields, models


class PlanDefinitionAction(models.Model):
    _inherit = "workflow.plan.definition.action"

    is_blocking = fields.Boolean(string="Is Blocking?", default=False)
