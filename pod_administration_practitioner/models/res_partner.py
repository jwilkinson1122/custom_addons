import logging

from odoo import _, api, fields, models
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    # FHIR Entity: Practitioner (https://www.hl7.org/fhir/practitioner.html)
    _inherit = "res.partner"

    is_practitioner = fields.Boolean(default=False)
    practitioner_role_ids = fields.Many2many(
        string="Practitioner Roles", comodel_name="pod.role"
    )  # FHIR Field: PractitionerRole/role
    practitioner_type = fields.Selection(
        string="Entity Type",
        selection=[
            ("internal", "Internal Entity"),
            ("external", "External Entity"),
        ],
        readonly=False,
    )

    @api.model
    def default_pod_fields(self):
        result = super(ResPartner, self).default_pod_fields()
        result.append("is_practitioner")
        return result

    def _check_pod(self, mode="write"):
        super()._check_pod(mode=mode)
        if (
            self.is_practitioner
            and mode != "read"
            and not self._check_pod_practitioner()
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

    def _check_pod_practitioner(self):
        return self.env.user.has_group(
            "pod_base.group_pod_configurator"
        )
