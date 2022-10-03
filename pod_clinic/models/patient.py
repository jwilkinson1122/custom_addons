# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Patient(models.Model):
    _name = 'pod_clinic.patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'rec_name'

    patient_id = fields.Char(string='ID', required=True, copy=False, readonly=True,
                             index=True, default=lambda self: _('New'))
    name = fields.Char(string='Name', required=True)
    rec_name = fields.Char(string='Recname',
                           compute='_compute_fields_rec_name')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], default='male', string="Gender", required=True)
    age = fields.Char(string='Age')
    description = fields.Text(string='Description')
    image = fields.Binary(string='Image', attachment=True)
    active = fields.Boolean(string="Active", default=True, tracking=True)
    color = fields.Integer(string="Color Index (0-15)")
    phone = fields.Char(string='Phone', required=True)
    email = fields.Char(string='Email')
    mobile = fields.Char(string="Mobile")
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street 2")
    country_id = fields.Many2one(
        comodel_name='res.country', string="Country",
        default=lambda self: self.env.company.country_id,
    )
    state_id = fields.Many2one(
        comodel_name='res.country.state', string="State",
        default=lambda self: self.env.company.state_id,
    )
    city = fields.Char(string="City")
    zip = fields.Char(string="ZIP Code")
    notes = fields.Text(string="Notes")
    partner_id = fields.Many2one(
        comodel_name='res.partner', string="Contact",
    )
    # Patient -> Type
    patient_type = fields.Many2one('pod_clinic.patient.type',
                                   string='Pathology')
    patient_type_name = fields.Char(related='patient_type.name',
                                    string='Pathology')

    # Patient -> Diagnosis
    patient_diagnosis = fields.Many2one('pod_clinic.patient.diagnosis', domain="[('patient_type','=',patient_type)]",
                                        string='Diagnosis')
    patient_diagnosis_name = fields.Char(related='patient_diagnosis.name',
                                         string='Diagnosis')

    # Owner
    owner = fields.Many2one(
        'pod_clinic.doctor', string='Owner', store=True, readonly=False)
    owner_id = fields.Integer(
        related='owner.id', string='Patient Owner ID')
    owner_name = fields.Char(
        related='owner.name', string='Owner Name')

    # Prescription
    # prescription = fields.One2many(
    #     'pod_clinic.prescription', 'owner', string='Prescription')
    # prescription_count = fields.Integer(compute='compute_prescription_count')

    # Appointment
    prescription_count = fields.Integer(compute='compute_prescription_count')

    @api.depends('name', 'patient_type_name', 'patient_diagnosis_name')
    def _compute_fields_rec_name(self):
        for patient in self:
            if(patient.patient_type_name == False and patient.patient_diagnosis_name == False):
                patient.rec_name = '{}'.format(patient.name)
            elif(patient.patient_diagnosis_name == False):
                patient.rec_name = '{} - {}'.format(patient.name,
                                                    patient.patient_type_name)
            elif(patient.patient_type_name == False):
                patient.rec_name = '{}'.format(patient.name)
            else:
                patient.rec_name = '{} - {} {}'.format(patient.name,
                                                       patient.patient_type_name, patient.patient_diagnosis_name)

    @api.model
    def create(self, vals):
        if vals.get('patient_id', _('New')) == _('New'):
            vals['patient_id'] = self.env['ir.sequence'].next_by_code(
                'patient.seq') or _('New')
        result = super(Patient, self).create(vals)
        return result

    # Button Patient Handle
    # @api.multi
    def open_patient_prescription(self):
        return {
            'name': _('Prescriptions'),
            'domain': [('patient', '=', self.id)],
            'view_type': 'form',
            'res_model': 'pod_clinic.prescription',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }
    # Button Patient Count

    def compute_prescription_count(self):
        for record in self:
            record.prescription_count = self.env['pod_clinic.prescription'].search_count(
                [('patient', '=', self.id)])


class PatientType(models.Model):
    _name = 'pod_clinic.patient.type'
    name = fields.Char(string='Name', required=True)


class PatientDiagnosis(models.Model):
    _name = 'pod_clinic.patient.diagnosis'
    name = fields.Char(string='Name', required=True)
    patient_type = fields.Many2one('pod_clinic.patient.type',
                                   string='Type', required=True)
