from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class PracticeDoctor(models.Model):
    _name = 'pod.manager.doctor'
    _description = 'Practice Doctor'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Doctor Name', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', 'Physician', required=True)
    # practice_id = fields.Many2one(
    #     'res.partner', domain=[('is_doctor', '=', True)], string='Medical Doctor')
    code = fields.Char('Id')
    info = fields.Text('Extra Info')
    # practice_id = fields.Char(string='Practice', tracking=True)
    address = fields.Char(string='Address', tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], default='male')
    phone = fields.Char(string='Phone', required=True, tracking=True)
    email = fields.Char(string='Email', required=True, tracking=True)
    department_id = fields.Many2one(
        "hr.department", string='Department', required=True, tracking=True)
    view_prescription_ids = fields.One2many('pod.manager.prescription', 'appointed_doctor_id', string="Prescription Count",
                                            readonly=True)
    age = fields.Integer(string='Age', required=True, tracking=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ], required=True, default='active', tracking=True)
    description = fields.Text()
    joined_from = fields.Date(string='Joined Date', tracking=True)
    image = fields.Binary(string='Image', attachment=True)
    total_prescriptions = fields.Integer(
        string='Total prescriptions', compute='_compute_prescriptions')

    def action_status_inactive(self):
        self.status = 'inactive'

    def action_status_active(self):
        self.status = 'active'

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
            record.total_prescriptions = self.env['pod.manager.prescription'].search_count(
                [('appointed_doctor_id', '=', record.id)])
