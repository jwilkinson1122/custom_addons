from odoo import api, fields, models

# FHIR Entity: Condition Code
# (http://hl7.org/fhir/valueset-condition-code.html)
    
class PodiatryClinicalFinding(models.Model):
    _name = "pod.clinical.finding"
    _inherit = "pod.abstract"
    _description = "Condition/Problem/Diagnosis codes"

    name = fields.Char(required=True)
    description = fields.Char()
    sct_code_id = fields.Many2one(
        comodel_name="pod.sct.concept",
        domain=[("is_clinical_finding", "=", True)],
    )
    create_warning = fields.Boolean(
        help="Mark if this clinical finding needs to create "
        "a warning for taking pod decisions"
    )

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"]
            .sudo()
            .next_by_code("pod.clinical.finding")
            or "/"
        )
