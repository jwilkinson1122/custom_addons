# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


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

    def _compute_coverage_template_count(self):
        for rec in self:
            rec.coverage_template_count = len(rec.coverage_template_ids)

    def action_view_coverage_template(self):
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "pod_financial_coverage.pod_coverage_template_action"
        )
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

    def _check_pod(self, mode="write"):
        super()._check_pod(mode=mode)

        if (
            self.is_payor
            and mode != "read"
            and not self.env.user.has_group(
                "pod_base.group_pod_financial"
            )
        ):
            _logger.info(
                "Access Denied by ACLs for operation: %s, uid: %s, model: %s",
                "write",
                self._uid,
                self._name,
            )
            raise AccessError(
                _(
                    "You are not allowed to %(mode)s pod Contacts (res.partner) records.",
                    mode=mode,
                )
            )
