import logging

from odoo import _, api, fields, models
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    # FHIR Entity: Person (http://hl7.org/fhir/person.html)
    _inherit = "res.partner"

    is_pod = fields.Boolean(default=False)
    patient_ids = fields.One2many("pod.patient", inverse_name="partner_id")

    @api.model
    def _get_pod_identifiers(self):
        """
        It must return a list of triads of check field, identifier field and
        defintion function
        :return: list
        """
        return []

    @api.model_create_multi
    def create(self, vals_list):
        partners = super(Partner, self).create(vals_list)
        for partner in partners:
            if partner.is_pod or partner.patient_ids:
                partner.check_pod("create")
        return partners

    def write(self, vals):
        result = super(Partner, self).write(vals)
        for partner in self:
            if partner.is_pod or partner.patient_ids:
                partner.check_pod("write")
        return result

    def unlink(self):
        for partner in self:
            if partner.is_pod or partner.sudo().patient_ids:
                partner.check_pod("unlink")
        return super(Partner, self).unlink()

    def check_pod(self, mode="write"):
        if self.env.su:
            return
        self._check_pod(mode=mode)

    def _check_pod(self, mode="write"):
        if self.sudo().patient_ids:
            self.sudo().patient_ids.check_access_rights(mode)
        if (
            self.is_pod
            and not self.env.user.has_group("pod_base.group_pod_user")
            and mode != "read"
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

    @api.model
    def default_pod_fields(self):
        return ["is_pod"]

    @api.model
    def default_get(self, fields_list):
        """We want to avoid to pass the pod_fields on the childs of the partner"""
        result = super(Partner, self).default_get(fields_list)
        for field in self.default_pod_fields():
            if result.get(field) and self.env.context.get("default_parent_id"):
                result[field] = False
        return result
