# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class PodiatryAllergySubstance(models.Model):

    _name = "pod.allergy.substance"
    _inherit = "pod.abstract"
    _description = "Substance/Pharmaceutical/Biological product codes"

    name = fields.Char(required=True)
    description = fields.Char()
    sct_code_id = fields.Many2one(
        comodel_name="pod.sct.concept",
        domain=[
            "|",
            ("is_clinical_substance", "=", True),
            ("is_pharmaceutical_product", "=", True),
        ],
    )
    create_warning = fields.Boolean(
        help="Mark if this allergy substance needs to create "
        "a warning for taking pod decisions"
    )

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"]
            .sudo()
            .next_by_code("pod.allergy.substance")
            or "/"
        )
