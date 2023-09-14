from odoo import fields, models


class PodiatryCondition(models.Model):

    _name = "pod.condition"
    _inherit = "pod.condition"

    origin_clinical_impression_id = fields.Many2one(
        comodel_name="pod.clinical.impression"
    )
    # This is used to keep track of the condition in case
    # the related impression is cancelled
