

import logging

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools import config

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    # FHIR Entity: Location (https://www.hl7.org/fhir/location.html)
    _inherit = "res.partner"

    is_practice = fields.Boolean(default=False)
    practice_id = fields.Many2one(
        "res.partner", domain=[("is_practice", "=", True)]
    )
    location_ids = fields.One2many("res.partner", inverse_name="practice_id")
    location_count = fields.Integer(compute="_compute_location_count")

    @api.depends("location_ids")
    def _compute_location_count(self):
        for record in self:
            record.location_count = len(record.location_ids)

    @api.constrains("is_location", "practice_id")
    def check_location_practice(self):
        test_condition = not config["test_enable"] or self.env.context.get(
            "test_check_location_practice"
        )
        if not test_condition:
            return
        for record in self:
            if record.is_location and not record.practice_id:
                raise ValidationError(
                    _("Practice must be fullfilled on locations")
                )

    @api.model
    def default_pod_fields(self):
        result = super(ResPartner, self).default_pod_fields()
        result.append("is_practice")
        return result

    def _check_pod(self, mode="write"):
        super()._check_pod(mode=mode)
        if (
            self.is_practice
            and mode != "read"
            and not self.env.user.has_group(
                "pod_base.group_pod_configurator"
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
