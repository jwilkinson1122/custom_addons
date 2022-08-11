
from odoo import fields, models


class PodAbstractConceptUniparent(models.AbstractModel):
    # Podiatry Code system concept

    _name = "pod.abstract.concept.uniparent"
    _inherit = "pod.abstract.concept"
    _description = "pod abstract concept uniparent"
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = "code"

    parent_id = fields.Many2one(
        comodel_name="pod.abstract.concept.uniparent", ondelete="cascade"
    )
    child_ids = fields.One2many(
        comodel_name="pod.abstract.concept.uniparent",
        inverse_name="parent_id",
    )
    parent_left = fields.Integer("Left Parent", index=True)
    parent_right = fields.Integer("Right Parent", index=True)
    parent_path = fields.Char(index=True)
