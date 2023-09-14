# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PodiatryEncounter(models.Model):
    _name = "pod.encounter"
    _inherit = ["pod.encounter", "mgmtsystem.quality.issue.abstract"]
