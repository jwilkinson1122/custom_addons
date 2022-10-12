from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class HospitalDoctor(models.Model):
    _name = 'kmhospital.doctor'
    _description = 'Podiatry Doctor'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Doctor Name', required=True, tracking=True)
    college = fields.Char(string='College', tracking=True)
    address = fields.Char(string='Address', tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], default='male')
    phone = fields.Char(string='Phone', required=True, tracking=True)
    email = fields.Char(string='Email', required=True, tracking=True)
    department_id = fields.Many2one(
        "hr.department", string='Department', required=True, tracking=True)
    view_prescription_ids = fields.One2many('kmhospital.eprescription', 'appointed_doctor_id', string="E-Prescription Count",
                                            readonly=True)
    age = fields.Integer(string='Age', required=True, tracking=True)
    status = fields.Selection([
        ('fulltime', 'Full time'),
        ('parttime', 'Part time')
    ], required=True, default='fulltime', tracking=True)
    description = fields.Text()
    joined_from = fields.Date(string='Joined Date', tracking=True)
    image = fields.Binary(string='Image', attachment=True)
    total_prescriptions = fields.Integer(
        string='Total prescriptions', compute='_compute_prescriptions')

    def action_status_halftime(self):
        self.status = 'parttime'

    def action_status_fulltime(self):
        self.status = 'fulltime'

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            valid_email = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
                                   record.email)

            if valid_email is None:
                raise ValidationError('Please provide a valid E-mail')

    @api.constrains('age')
    def _check_doctor_age(self):
        for record in self:
            if record.age <= 0:
                raise ValidationError('Age must be greater than 0')

    # same as view_prescription_ids but implemented using computed fields
    # compute prescriptions of individual doctor
    def _compute_prescriptions(self):
        for record in self:
            record.total_prescriptions = self.env['kmhospital.eprescription'].search_count(
                [('appointed_doctor_id', '=', record.id)])
