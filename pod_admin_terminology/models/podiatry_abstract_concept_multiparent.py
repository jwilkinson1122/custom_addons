

from odoo import api, fields, models


class PodiatryAbstractConceptMultiparent(models.AbstractModel):
    # Podiatry Code system concept
    # (https://www.hl7.org/fhir/codesystem.html)
    _name = "podiatry.abstract.concept.multiparent"
    _inherit = "podiatry.abstract.concept"
    _description = "podiatry abstract concept multiparent"

    parent_ids = fields.Many2many(
        comodel_name="podiatry.abstract.concept",
        relation="podiatry_abstract_concept_is_a",
        column1="parent",
        column2="child",
    )
    child_ids = fields.Many2many(
        comodel_name="podiatry.abstract.concept", compute="_compute_child_ids"
    )  # Field: concept/concept
    full_parent_ids = fields.Many2many(
        comodel_name="podiatry.abstract.concept", compute="_compute_child_ids"
    )
    full_child_ids = fields.Many2many(
        comodel_name="podiatry.abstract.concept",
        compute="_compute_full_child_ids",
    )

    def _get_childs(self):
        res = self.child_ids.ids or []
        for child in self.child_ids:
            res += child._get_childs()
        return res

    @api.depends("parent_ids")
    def _compute_full_child_ids(self):
        for record in self:
            record.full_child_ids = record.browse(record._get_childs())

    @api.depends("parent_ids")
    def _compute_child_ids(self):
        for record in self:
            record.child_ids = self.search([("parent_ids", "=", record.id)])
            full_parents = record.parent_ids.ids or []
            for parent in record.parent_ids:
                full_parents += parent.full_parent_ids.ids
            record.full_parent_ids = record.browse(full_parents)
