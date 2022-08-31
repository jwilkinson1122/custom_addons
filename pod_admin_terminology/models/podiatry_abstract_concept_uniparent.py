

from odoo import fields, models


class PodiatryAbstractConceptUniparent(models.AbstractModel):
    # Podiatry Code system concept
    # (https://www.hl7.org/fhir/codesystem.html)
    _name = "podiatry.abstract.concept.uniparent"
    _inherit = "podiatry.abstract.concept"
    _description = "podiatry abstract concept uniparent"
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = "code"

    parent_id = fields.Many2one(
        comodel_name="podiatry.abstract.concept.uniparent", ondelete="cascade"
    )  # SNOMED_CT Field: parent
    child_ids = fields.One2many(
        comodel_name="podiatry.abstract.concept.uniparent",
        inverse_name="parent_id",
    )  # SNOMED_CT Field: parent
    parent_left = fields.Integer("Left Parent", index=True)
    parent_right = fields.Integer("Right Parent", index=True)
    parent_path = fields.Char(index=True)
