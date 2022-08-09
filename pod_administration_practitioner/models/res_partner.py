

from odoo import api, fields, models
from odoo.modules import get_module_resource


class ResPartner(models.Model):

    _inherit = "res.partner"
    is_practitioner = fields.Boolean(default=True, string='Doctor')
    # is_physician = fields.Boolean(string='Is Physician')
    # is_practitioner = fields.Boolean(default=False)
    is_patient = fields.Boolean(string='Patient')
    # speciality = fields.Many2one('physician.speciality', string='Speciality')
    is_practice = fields.Many2one('res.partner', string='Medical Practice')

    practitioner_role_ids = fields.Many2many(
        string="Clinical Roles", comodel_name="pod.role")

    practitioner_type = fields.Selection(
        string="Entity Type",
        selection=[
            ("internal", "Internal Entity"),
            ("external", "External Entity"),
        ],
        readonly=False,
    )
    practitioner_identifier = fields.Char(
        readonly=True
    )

    @api.model
    def _get_pod_identifiers(self):
        res = super(ResPartner, self)._get_pod_identifiers()
        res.append(
            (
                "is_pod",
                "is_practitioner",
                "practitioner_identifier",
                self._get_practitioner_identifier,
            )
        )
        return res

    @api.model
    def _get_practitioner_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("pod.practitioner") or "ID"
        )

    @api.model
    def _get_default_image_path(self, vals):
        if vals.get("is_practitioner", False):
            return get_module_resource(
                "pod_administration_practitioner",
                "static/src/img",
                "user_avatar.jpg",
            )

    @api.model
    def default_pod_fields(self):
        result = super(ResPartner, self).default_pod_fields()
        result.append("is_practitioner")
        return result
