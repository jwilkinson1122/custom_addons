# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    _description = "Hr Employee"

    staff_type = fields.Selection(
        [('doctor', 'Doctor'), ('receptionist', 'Receptionist'), ('nurse', 'Nurse'), ('administrator', 'Administrator'),
         ('other', 'Other')], string='Employee Type', tracking=True)
    degree_id = fields.Many2one('employee.degree', string='Degree')
