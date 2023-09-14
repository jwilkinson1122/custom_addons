from odoo import fields, models


class PodiatryCoverage(models.Model):

    _inherit = "pod.coverage"

    subscriber_magnetic_str = fields.Char(readonly=True)
