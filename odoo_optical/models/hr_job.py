# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrJob(models.Model):
    _inherit = 'hr.job'

    is_optometrist = fields.Boolean(default=False, string="Is Optometrist")

