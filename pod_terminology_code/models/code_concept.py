
from odoo import fields, models


class CodeConcept(models.Model):
    """
    Podiatry Clinical Terms concept

    """

    _name = "code.concept"
    _inherit = "pod.abstract.concept.multiparent"
    _description = "Podiatry Code Concept"

    parent_ids = fields.Many2many(
        comodel_name="code.concept", relation="code_concept_is_a"
    )
    child_ids = fields.Many2many(comodel_name="code.concept")
    full_parent_ids = fields.Many2many(comodel_name="code.concept")
    full_child_ids = fields.Many2many(comodel_name="code.concept")

    def check_property(self, name, code):
        for parent in self.parent_ids:
            if parent[name] or parent.code in code:
                return True
