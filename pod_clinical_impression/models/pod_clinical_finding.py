from odoo import fields, models


class PodiatryClinicalFinding(models.Model):

    _inherit = "pod.clinical.finding"

    create_condition_from_clinical_impression = fields.Boolean(
        help="If marked, "
        "when this clinical finding is added to a clinical impression,"
        "it will create automatically a condition for the corresponding patient"
    )
