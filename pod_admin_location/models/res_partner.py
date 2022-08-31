

from odoo import api, fields, models


class ResPartner(models.Model):
    # : Location (https://www.hl7.org/fhir/location.html)
    _inherit = "res.partner"

    is_location = fields.Boolean(default=False)
    location_identifier = fields.Char(readonly=True)  # Field: identifier
    description = fields.Text(string="Description")  # field: description

    @api.model
    def _get_podiatry_identifiers(self):
        res = super(ResPartner, self)._get_podiatry_identifiers()
        res.append(
            (
                "is_prescription",
                "is_location",
                "location_identifier",
                self._get_location_identifier,
            )
        )
        return res

    @api.model
    def _get_location_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("podiatry.location") or "LOC"

    @api.model
    def default_podiatry_fields(self):
        result = super(ResPartner, self).default_podiatry_fields()
        result.append("is_location")
        return result
