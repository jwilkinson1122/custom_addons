

from odoo import api, fields, models


class PodiatryRequestGroupChangePlan(models.TransientModel):
    _name = "pod.request.group.change.plan"
    _description = "pod.request.group.change.plan"

    request_group_id = fields.Many2one(
        "pod.request.group", required=True, readonly=True
    )
    careplan_id = fields.Many2one(
        "pod.careplan",
        related="request_group_id.careplan_id",
        readonly=True,
    )
    patient_id = fields.Many2one(
        "pod.patient", related="request_group_id.patient_id", readonly=True
    )
    coverage_id = fields.Many2one(
        "pod.coverage", readonly=True, related="careplan_id.coverage_id"
    )
    practice_id = fields.Many2one(
        "res.partner", related="careplan_id.practice_id", readonly=True
    )
    coverage_template_id = fields.Many2one(
        "pod.coverage.template",
        readonly=True,
        related="coverage_id.coverage_template_id",
    )
    agreement_ids = fields.Many2many(
        "pod.coverage.agreement", compute="_compute_agreements"
    )
    agreement_line_id = fields.Many2one(
        "pod.coverage.agreement.item",
        domain="[('coverage_agreement_id', 'in', agreement_ids),"
        "('plan_definition_id', '!=', False)]",
    )
    product_id = fields.Many2one(
        "product.product",
        readonly=True,
        related="agreement_line_id.product_id",
    )
    plan_definition_id = fields.Many2one(
        comodel_name="workflow.plan.definition",
        readonly=True,
        related="agreement_line_id.plan_definition_id",
    )
    authorization_method_id = fields.Many2one(
        "pod.authorization.method",
        readonly=True,
        related="agreement_line_id.authorization_method_id",
    )
    authorization_format_id = fields.Many2one(
        "pod.authorization.format",
        readonly=True,
        related="agreement_line_id.authorization_format_id",
    )
    authorization_required = fields.Boolean(
        readonly=True,
        related="agreement_line_id.authorization_method_id." "authorization_required",
    )
    authorization_number = fields.Char()
    authorization_number_extra_1 = fields.Char()
    authorization_information = fields.Text(
        related="agreement_line_id.authorization_format_id."
        "authorization_information",
        readonly=True,
    )
    authorization_extra_1_information = fields.Text(
        related="authorization_format_id.authorization_extra_1_information",
        readonly=True,
    )
    requires_authorization_extra_1 = fields.Boolean(
        related="authorization_format_id.requires_authorization_extra_1",
        readonly=True,
    )

    @api.depends("coverage_template_id", "practice_id")
    def _compute_agreements(self):
        for rec in self:
            rec.agreement_ids = self.env["pod.coverage.agreement"].search(
                [
                    (
                        "coverage_template_ids",
                        "=",
                        rec.coverage_template_id.id,
                    ),
                    ("practice_ids", "=", rec.practice_id.id),
                ]
            )

    def run(self):
        self.ensure_one()
        self.request_group_id.change_plan_definition(self.agreement_line_id)
        return {}
