from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class PracticePatient(models.Model):
    _name = 'pod_erp.patient'
    _description = 'Practice Patient'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Patient Name', required=True, tracking=True)
    address = fields.Char(string='Address', tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], default="male", tracking=True)
    phone = fields.Char(string='Phone', required=True, tracking=True)
    age = fields.Integer(string='Age', required=True, tracking=True)
    email = fields.Char(string='Email', tracking=True)
    primary_doctor_id = fields.Many2one("res.partner", string="Doctor name", required=True)
    patient_prescription_ids = fields.One2many('pod_erp.prescription', 'patient_id', string="Prescription Count",
                                              readonly=True)
    total_prescriptions = fields.Integer(string='No. of prescriptions', compute='_compute_prescriptions')

    # check if the patient is already exists based on the patient name and phone number
    @api.constrains('name', 'phone')
    def _check_patient_exists(self):
        for record in self:
            patient = self.env['pod_erp.patient'].search(
                [('name', '=', record.name), ('phone', '=', record.phone), ('id', '!=', record.id)])
            if patient:
                raise ValidationError(f'Patient {record.name} already exists')

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            valid_email = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
                                   record.email)
            if valid_email is None:
                raise ValidationError('Please provide a valid Email')

    @api.constrains('age')
    def _check_patient_age(self):
        for record in self:
            if record.age <= 0:
                raise ValidationError('Age must be greater than 0')

    # compute prescriptions of individual patient
    def _compute_prescriptions(self):
        for record in self:
            record.total_prescriptions = self.env['pod_erp.prescription'].search_count(
                [('patient_id', '=', record.id)])

    def action_url(self):
        return {
            "type": "ir.actions.act_url",
            "url": "https://github.com/KamrulSh/pod_erp",
            "target": "new",
        }
