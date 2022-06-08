
from odoo import api, fields, models


class ResPartner(models.Model):
    # FHIR Entity: Payor
    # (https://www.hl7.org/fhir/coverage-definitions.html#Coverage.payor)
    _inherit = "res.partner"

    is_payor = fields.Boolean(default=False)
    payor_identifier = fields.Char(readonly=True)  # FHIR Field: identifier
    coverage_template_ids = fields.One2many(
        string="Coverage Template",
        comodel_name="pod.coverage.template",
        inverse_name="payor_id",
    )
    coverage_template_count = fields.Integer(
        compute="_compute_coverage_template_count",
        string="# of Templates",
        copy=False,
        default=0,
    )

    @api.model
    def _get_pod_identifiers(self):
        res = super(ResPartner, self)._get_pod_identifiers()
        res.append(
            (
                "is_pod",
                "is_payor",
                "payor_identifier",
                self._get_payor_identifier,
            )
        )
        return res

    def _compute_coverage_template_count(self):
        for rec in self:
            rec.coverage_template_count = len(rec.coverage_template_ids)

    @api.model
    def _get_payor_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("pod.payor") or "/"

    def action_view_coverage_template(self):
        action = self.env.ref(
            "pod_financial_coverage.pod_coverage_template_action"
        )
        result = action.read()[0]
        result["context"] = {"default_payor_id": self.id}
        result["domain"] = "[('payor_id', '=', " + str(self.id) + ")]"
        if len(self.coverage_template_ids) == 1:
            res = self.env.ref("pod.coverage.template.view.form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = self.coverage_template_ids.id
        return result

    @api.model
    def default_pod_fields(self):
        result = super(ResPartner, self).default_pod_fields()
        result.append("is_payor")
        return result
