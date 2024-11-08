from odoo import models, fields

class Shift(models.Model):
    _name = 'staff.shift'
    _description = 'Staff Shift'

    staff_id = fields.Many2one('staff.management', string='Staff', required=True)
    shift_type = fields.Selection([
        ('morning', 'Morning Shift'),
        ('evening', 'Evening Shift'),
        ('night', 'Night Shift'),
    ], string='Shift Type', required=True)
    start_time = fields.Float(string='Start Time', required=True)
    end_time = fields.Float(string='End Time', required=True)
