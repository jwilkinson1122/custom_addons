from odoo import fields, models


class PodiatryCoverageAgreementItem(models.Model):
    _inherit = "pod.coverage.agreement.item"

    def _default_authorization_method(self):
        agreement_id = self.env.context.get("default_coverage_agreement_id", False)
        agreement = self.env["pod.coverage.agreement"].browse(agreement_id)
        if agreement:
            return agreement.authorization_method_id

    def _default_authorization_format(self):
        agreement_id = self.env.context.get("default_coverage_agreement_id", False)
        agreement = self.env["pod.coverage.agreement"].browse(agreement_id)
        if agreement:
            return agreement.authorization_format_id

    coverage_template_ids = fields.Many2many(
        string="Coverage Templates",
        comodel_name="pod.coverage.template",
        related="coverage_agreement_id.coverage_template_ids",
        readonly=True,
    )
    authorization_method_id = fields.Many2one(
        "pod.authorization.method",
        default=_default_authorization_method,
        required=True,
    )
    authorization_format_id = fields.Many2one(
        "pod.authorization.format",
        default=_default_authorization_format,
        required=True,
    )
    date_from = fields.Date(
        "From",
        related="coverage_agreement_id.date_from",
        store=True,
        readonly=True,
    )
    date_to = fields.Date(
        "To",
        related="coverage_agreement_id.date_to",
        store=True,
        readonly=True,
    )

    def _check_authorization(
        self,
        method,
        authorization_number=False,
        authorization_number_extra_1=False,
        **kwargs
    ):
        vals = {
            "authorization_number": authorization_number,
            "authorization_status": "authorized",
            "authorization_method_id": method.id,
            "authorization_number_extra_1": authorization_number_extra_1,
        }
        auth_format = self.authorization_format_id
        if method.authorization_required and not auth_format.check_value(
            authorization_number=authorization_number,
            authorization_number_extra_1=authorization_number_extra_1,
        ):
            vals["authorization_status"] = "pending"
        return vals

    def _copy_agreement_vals(self, agreement):
        res = super()._copy_agreement_vals(agreement)
        res["authorization_method_id"] = self.authorization_method_id.id
        res["authorization_format_id"] = self.authorization_format_id.id
        return res

    def get_item(self, product, coverage_template, center, date=False, plan=False):
        if not date:
            date = fields.Date.today()
        if isinstance(product, int):
            product_id = product
        else:
            product_id = product.id
        if isinstance(center, int):
            center_id = center
        else:
            center_id = center.id
        if isinstance(coverage_template, int):
            coverage_template_id = coverage_template
        else:
            coverage_template_id = coverage_template.id
        domain = [
            ("coverage_agreement_id.center_ids", "=", center_id),
            ("product_id", "=", product_id),
            ("coverage_template_ids", "=", coverage_template_id),
            "|",
            ("date_from", "=", False),
            ("date_from", "<=", date),
            "|",
            ("date_to", "=", False),
            ("date_to", ">=", date),
        ]
        if plan:
            domain.append(("plan_definition_id", "!=", False))
        return self.search(domain, limit=1)
