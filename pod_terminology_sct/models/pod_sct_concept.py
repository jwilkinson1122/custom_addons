

from odoo import fields, models


class PodiatrySCTConcept(models.Model):
    """
    Podiatry SNOMED CT concept
    (https://www.hl7.org/fhir/codesystem-snomedct.html)
    It has been defined following the code system entity with the following
    information:
    - url: http://snomed.info/sct
    - identifier: urn:ietf:rfc:3986 / urn:oid:2.16.840.1.113883.6.96
    - name: SNOMED_CT
    - publisher: IHTSDO
    """

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
