from odoo import models, fields, api

class Staff(models.Model):
    _name = 'staff.management'
    _description = 'Staff Management'

    name = fields.Char(string='Name', required=True)
    job_title = fields.Selection([
        ('nurse', 'Nurse'),
        ('technician', 'Technician'),
        ('admin', 'Admin'),
    ], string='Job Title', required=True)
    email = fields.Char(string='Email', required=True)
    contact_number = fields.Char(string='Contact Number')
    shift_ids = fields.One2many('staff.shift', 'staff_id', string='Shifts')
    attendance_ids = fields.One2many('staff.attendance', 'staff_id', string='Attendance Records')
    active = fields.Boolean(string='Active', default=True)
