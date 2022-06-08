
from odoo import api, fields, models
from odoo.modules import get_module_resource

class ResPartner(models.Model):

    _inherit = "res.partner"

    is_location = fields.Boolean(default=False)


    # location_type = fields.Selection(
    #     string="Entity Type",
    #     selection=[
    #         ("parent", "Parent Entity"),
    #         ("child", "Child Entity"),
    #     ],
    #     readonly=False,
    # )

    location_relationship_ids = fields.Many2many(
        string="Practice Location Relationship", comodel_name="pod.location.relationship"
    )

    location_identifier = fields.Char(readonly=True)
    description = fields.Text(string="Description")


    @api.model
    def _get_pod_identifiers(self):
        res = super(ResPartner, self)._get_pod_identifiers()
        res.append(
            (
                "is_pod",
                "is_location",
                "location_identifier",
                self._get_location_identifier,
            )
        )
        return res

    @api.model
    def _get_location_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("pod.location") or "ID"

    @api.model
    def default_pod_fields(self):
        result = super(ResPartner, self).default_pod_fields()
        result.append("is_location")
        return result


# class PodAbstract(models.AbstractModel):
#     # default entity, as all models have internal_identifiers
#     _name = "pod.abstract"
#     _description = "Default entity"

#     internal_identifier = fields.Char(
#         name="Identifier",
#         help="Internal identifier used to identify this record",
#         readonly=True,
#         default="ID",
#         copy=False,
#     )

#     @api.model
#     def create(self, vals):
#         vals_upd = vals.copy()
#         if vals_upd.get("internal_identifier", "ID") == "ID":
#             vals_upd["internal_identifier"] = self._get_internal_identifier(
#                 vals_upd
#             )
#         return super(PodAbstract, self).create(vals_upd)

#     def _get_internal_identifier(self, vals):
#
#         raise UserError(_("Function is not defined"))
