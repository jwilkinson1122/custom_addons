from odoo import models, fields

class Attendance(models.Model):
    _name = 'staff.attendance'
    _description = 'Staff Attendance'

    staff_id = fields.Many2one('staff.management', string='Staff', required=True)
    date = fields.Date(string='Date', required=True)
    check_in = fields.Float(string='Check In Time', required=True)
    check_out = fields.Float(string='Check Out Time', required=True)
    hours_worked = fields.Float(compute='_compute_hours_worked', string='Hours Worked')

    def _compute_hours_worked(self):
        for record in self:
            record.hours_worked = record.check_out - record.check_in
