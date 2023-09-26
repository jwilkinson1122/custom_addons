

from odoo import fields, models


class PodiatryProcedureRequest(models.Model):
    _inherit = "pod.procedure.request"

    variable_fee = fields.Float(
        string="Variable fee (%)",
        default="0.0",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    fixed_fee = fields.Float(
        string="Fixed fee",
        default="0.0",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    pod_commission = fields.Boolean(
        related="service_id.pod_commission", readonly=True
    )

    def _get_procedure_values(self):
        res = super(PodiatryProcedureRequest, self)._get_procedure_values()
        res.update(
            {
                "service_id": self.service_id.id,
                "variable_fee": self.variable_fee,
                "fixed_fee": self.fixed_fee,
            }
        )
        conditions = self.performer_id.practitioner_condition_ids
        practitioner_condition_id = conditions.get_condition(
            self.request_group_id.service_id, self.service_id, self.practice_id
        )
        if practitioner_condition_id:
            res.update({"practitioner_condition_id": practitioner_condition_id.id})
        return res

    def generate_event(self, *args, **kwargs):
        res = super().generate_event(*args, **kwargs)
        res.sudo().compute_commission(res.procedure_request_id)
        return res

    def _update_related_activity_vals(self, vals, parent, plan, action):
        res = super()._update_related_activity_vals(vals, parent, plan, action)
        res.update(
            {
                "variable_fee": action.variable_fee,
                "fixed_fee": action.fixed_fee,
            }
        )
        return res
