# models/doctor.py
from odoo import models, fields, api

class Doctor(models.Model):
    _name = 'hospital.doctor'
    _description = 'Doctor'
    
    name = fields.Char(string='Name', required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender', required=True)
    contact_number = fields.Char(string='Contact Number')
    email = fields.Char(string='Email')
    specialization_id = fields.Many2one('hospital.specialization', string='Specialization', required=True)
    schedule_ids = fields.One2many('hospital.schedule', 'doctor_id', string='Schedules')
    availability = fields.Selection([
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
    ], string='Availability', default='available')
    color = fields.Integer()  # Used for kanban card color

    # Smart button for schedules
    schedule_count = fields.Integer(compute='_compute_schedule_count', string='Schedule Count')

    @api.depends('schedule_ids')
    def _compute_schedule_count(self):
        for doctor in self:
            doctor.schedule_count = len(doctor.schedule_ids)

    # Method for a smart button
    def action_view_schedules(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Schedules',
            'view_mode': 'tree,form',
            'res_model': 'hospital.schedule',
            'domain': [('doctor_id', '=', self.id)],
        }
