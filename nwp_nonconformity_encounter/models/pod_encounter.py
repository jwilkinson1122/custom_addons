

from odoo import models


class PodiatryEncounter(models.Model):
    _name = "pod.encounter"
    _inherit = ["pod.encounter", "mgmtsystem.quality.issue.abstract"]
