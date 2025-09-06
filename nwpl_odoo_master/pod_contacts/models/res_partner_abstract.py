from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResPartnerAbstract(models.AbstractModel):
    _name = "res.partner.abstract"
    _description = "Default entity"

    partner_identifier = fields.Char(
        name="Identifier",
        help="Internal identifier used to identify this record",
        readonly=True,
        default="New",
        copy=False,
    )

    @api.model
    def create(self, vals):
        vals_upd = vals.copy()
        if vals_upd.get("partner_identifier", "New") == "New":
            vals_upd["partner_identifier"] = self._get_partner_identifier(vals_upd)
            return super().create(vals_upd)

    def _get_partner_identifier(self, vals):
        raise UserError(_("Function is not defined"))
