# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_optometrist = fields.Boolean(readonly=True, related="job_id.is_optometrist")

