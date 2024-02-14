# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TaskOrthoticProblem(models.Model):
    """Task Orthotic Problem"""
    _name = 'task.orthotic.problem'
    _description = __doc__
    _rec_name = 'description'

    is_check = fields.Boolean(string="Check")
    description = fields.Char(string="Description", required=True)
    remarks = fields.Char(string="Remarks")
    project_task_id = fields.Many2one('project.task')

    @api.onchange('is_check')
    def task_orthotic_problem_check(self):
        for rec in self:
            if rec.is_check:
                rec.description = rec.description
            else:
                rec.description = False
