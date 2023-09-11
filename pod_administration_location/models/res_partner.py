import logging

from odoo import _, api, fields, models
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)

# FHIR Entity: Location (https://www.hl7.org/fhir/location.html)

class ResPartner(models.Model):
    _inherit = "res.partner"

    is_location = fields.Boolean(default=False)

    @api.model
    def default_pod_fields(self):
        result = super(ResPartner, self).default_pod_fields()
        result.append("is_location")
        return result

    def _check_pod(self, mode="write"): 
        super()._check_pod(mode=mode)
        if (
            self.is_location
            and mode != "read"
            and not self.env.user.has_group("pod_base.group_pod_configurator")
        ):
            _logger.info(
                "Access Denied by ACLs for operation: %s, uid: %s, model: %s",
                "write",
                self._uid,
                self._name,
            )
            raise AccessError(
                _(
                    "You are not allowed to %(mode)s pod Contacts (res.partner) records.", mode=mode,
                )
            )
