
import logging

from odoo import _, api, fields, models
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    # FHIR Entity: Practitioner (https://www.hl7.org/fhir/practitioner.html)
    _inherit = "res.partner"

    is_practitioner = fields.Boolean(default=False)
    practitioner_role_ids = fields.Many2many(
        string="Practitioner Roles", comodel_name="podiatry.role"
    )  # FHIR Field: PractitionerRole/role
    # entity_type = fields.Selection(
    #     string="Entity Type",
    #     selection=[
    #         ("internal", "Internal Entity"),
    #         ("external", "External Entity"),
    #     ],
    #     readonly=False,
    # )

    @api.model
    def default_podiatry_fields(self):
        result = super(ResPartner, self).default_podiatry_fields()
        result.append("is_practitioner")
        return result

    def _check_podiatry(self, mode="write"):
        super()._check_podiatry(mode=mode)
        if (
            self.is_location
            and mode != "read"
            and not self.env.user.has_group(
                "podiatry_base.group_podiatry_configurator"
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
                    "You are not allowed to %(mode)s podiatry Contacts (res.partner) records.",
                    mode=mode,
                )
            )
