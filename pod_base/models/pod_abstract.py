
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class PodiatryAbstract(models.AbstractModel):
    # FHIR Entity: default entity, as all models have internal_identifiers
    _name = "pod.abstract"
    _description = "Default FHIR entity"

    internal_identifier = fields.Char(
        name="Identifier",
        help="Internal identifier used to identify this record",
        readonly=True,
        default="/",
        copy=False,
    )  # FHIR Field: identifier

    @api.model
    def create(self, vals):
        vals_upd = vals.copy()
        if vals_upd.get("internal_identifier", "/") == "/":
            vals_upd["internal_identifier"] = self._get_internal_identifier(
                vals_upd
            )
            return super().create(vals_upd)
        # return super(PodiatryAbstract, self).create(vals_upd)
 

    def _get_internal_identifier(self, vals):
        _logger.info("Executing _get_internal_identifier in pod.abstract")
        # It should be rewritten for each element
        raise UserError(_("Function is not defined"))
