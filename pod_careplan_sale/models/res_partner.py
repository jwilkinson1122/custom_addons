import logging

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)


# FHIR Entity: Payor
# (https://www.hl7.org/fhir/coverage-definitions.html#Coverage.payor)

class ResPartner(models.Model):
    _inherit = "res.partner"

    is_sub_payor = fields.Boolean(default=False)
    payor_id = fields.Many2one(
        "res.partner", string="Payor", domain=[("is_payor", "=", True)]
    )
    sub_payor_ids = fields.One2many("res.partner", inverse_name="payor_id")
    show_patient = fields.Boolean()
    show_subscriber = fields.Boolean()
    show_authorization = fields.Boolean()
    invoice_nomenclature_id = fields.Many2one(
        "product.nomenclature",
        "Nomenclature", help="Nomenclature for invoices",
    )

    @api.constrains("is_sub_payor", "payor_id")
    def _check_subpayor(self):
        for record in self:
            if record.is_sub_payor and not record.payor_id:
                raise ValidationError(_("Payor is required on subpayors"))

    @api.model
    def default_pod_fields(self):
        result = super(ResPartner, self).default_pod_fields()
        result.append("is_sub_payor")
        return result
    
    def _check_pod(self, mode="write"):
        super()._check_pod(mode=mode)
        if (
            self.is_sub_payor
            and mode != "read"
            and not self.env.user.has_group("pod_base.group_pod_financial")
        ):
            _logger.info(
                "Access Denied by ACLs for operation: %s, uid: %s, model: %s",
                "write",
                self._uid,
                self._name,
            )
            raise AccessError(
                _(
                    "You are not allowed to %(mode)s Contacts (res.partner) records.",
                    mode=mode,
                )
            )

   