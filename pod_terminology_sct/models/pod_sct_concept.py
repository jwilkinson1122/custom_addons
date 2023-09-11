from odoo import fields, models


class PodiatrySCTConcept(models.Model):
    _name = "pod.sct.concept"
    _inherit = "pod.abstract.concept.multiparent"
    _description = "Podiatry SCT Concept"

    parent_ids = fields.Many2many(
        comodel_name="pod.sct.concept", relation="pod_sct_concept_is_a"
    )
    child_ids = fields.Many2many(comodel_name="pod.sct.concept")
    full_parent_ids = fields.Many2many(comodel_name="pod.sct.concept")
    full_child_ids = fields.Many2many(comodel_name="pod.sct.concept")

    def check_property(self, name, codes):
        for parent in self.parent_ids:
            if parent[name] or parent.code in codes:
                return True
