

from odoo import api, fields, models


class PodiatryRequestGroupCheckAuthorization(models.TransientModel):
    _name = "pod.request.group.check.authorization"
    _description = "pod.request.group.check.authorization"

    @api.model
    def _default_request(self):
        return self.env["pod.request.group"].browse(
            self.env.context.get("default_request_group_id", False)
        )

    @api.model
    def _default_method(self):
        return (
            self._default_request().coverage_agreement_item_id.authorization_method_id
        )

    request_group_id = fields.Many2one("pod.request.group", required=True)
    coverage_agreement_item_id = fields.Many2one(
        "pod.coverage.agreement.item",
        readonly=True,
        related="request_group_id.coverage_agreement_item_id",
    )
    product_id = fields.Many2one(
        "product.product",
        readonly=True,
        related="coverage_agreement_item_id.product_id",
    )
    plan_definition_id = fields.Many2one(
        comodel_name="workflow.plan.definition",
        readonly=True,
        related="coverage_agreement_item_id.plan_definition_id",
    )
    authorization_number = fields.Char()
    authorization_number_extra_1 = fields.Char()
    authorization_method_id = fields.Many2one(
        "pod.authorization.method",
        default=_default_method,
        domain="[('id', 'in', authorization_method_ids)]",
    )
    authorization_method_ids = fields.Many2many(
        "pod.authorization.method",
        compute="_compute_authorization_method_ids",
        string="Authorization Methods",
    )
    authorization_format_id = fields.Many2one(
        "pod.authorization.format",
        related="coverage_agreement_item_id.authorization_format_id",
        readonly=True,
    )
    authorization_information = fields.Text(
        related="authorization_format_id.authorization_information",
        readonly=True,
    )
    authorization_required = fields.Boolean(
        related="authorization_method_id.authorization_required", readonly=True
    )
    authorization_extra_1_information = fields.Text(
        related="authorization_format_id.authorization_extra_1_information",
        readonly=True,
    )
    requires_authorization_extra_1 = fields.Boolean(
        related="authorization_format_id.requires_authorization_extra_1",
        readonly=True,
    )

    @api.depends("request_group_id")
    def _compute_authorization_method_ids(self):
        for rec in self:
            result = self.env["pod.authorization.method"]
            method = self.coverage_agreement_item_id.authorization_method_id
            while method:
                result |= method
                method = method.auxiliary_method_id
            rec.authorization_method_ids = result

    def _get_kwargs(self):
        return {
            "authorization_number": self.authorization_number,
            "authorization_number_extra_1": self.authorization_number_extra_1,
            "authorization_method_id": self.authorization_method_id.id,
        }

    def run(self):
        self.ensure_one()
        self.request_group_id.change_authorization(
            self.authorization_method_id, **self._get_kwargs()
        )
        return {}
