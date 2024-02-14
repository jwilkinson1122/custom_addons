# -*- coding: utf-8 -*-
from odoo import models, fields, api


class DiagnosedProblem(models.Model):
    """Diagnosed Problem"""
    _name = 'diagnosed.problem'
    _description = __doc__
    _rec_name = 'problem_name'

    is_check = fields.Boolean(string="Check")
    problem_name = fields.Char(string="Problem", required=True)
    orthotic_repair_order_id = fields.Many2one('orthotic.repair.order')

    @api.onchange('is_check')
    def problem_checklist_check(self):
        for rec in self:
            if rec.is_check:
                rec.problem_name = rec.problem_name
            else:
                rec.problem_name = False
