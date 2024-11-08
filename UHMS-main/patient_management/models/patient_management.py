# models/patient_management.py
from odoo import models, fields

class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Hospital Patient'

    name = fields.Char(string='Patient Name', required=True)
    dob = fields.Date(string='Date of Birth', required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender')
    contact_number = fields.Char(string='Contact Number')
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')
    medical_history_ids = fields.One2many('hospital.medical.history', 'patient_id', string='Medical Histories')
    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string='Appointments')
    treatment_ids = fields.One2many('hospital.treatment', 'patient_id', string='Treatments')
    surgery_ids = fields.One2many('hospital.surgery', 'patient_id', string='Surgeries')
    lab_test_ids = fields.One2many('hospital.lab.test', 'patient_id', string='Lab Tests')

class HospitalMedicalHistory(models.Model):
    _name = 'hospital.medical.history'
    _description = 'Medical History'

    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    date = fields.Date(string='Date', required=True)
    description = fields.Text(string='Description')
    diagnosis = fields.Text(string='Diagnosis')
    treatment_ids = fields.One2many('hospital.treatment', 'medical_history_id', string='Treatments')

class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Appointment'

    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    doctor_id = fields.Many2one('hr.employee', string='Doctor', required=True)
    appointment_date = fields.Datetime(string='Appointment Date', required=True)
    reason = fields.Text(string='Reason for Visit')
    status = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ], string='Status', default='scheduled')

class HospitalTreatment(models.Model):
    _name = 'hospital.treatment'
    _description = 'Treatment'

    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    medical_history_id = fields.Many2one('hospital.medical.history', string='Medical History')
    date = fields.Date(string='Date', required=True)
    description = fields.Text(string='Description')
    medication_ids = fields.Many2many('product.product', string='Medications')
    notes = fields.Text(string='Notes')

class HospitalSurgery(models.Model):
    _name = 'hospital.surgery'
    _description = 'Surgery'

    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    date = fields.Date(string='Date', required=True)
    description = fields.Text(string='Description')
    surgeon_id = fields.Many2one('hr.employee', string='Surgeon', required=True)
    notes = fields.Text(string='Notes')

class HospitalLabTest(models.Model):
    _name = 'hospital.lab.test'
    _description = 'Lab Test'

    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    test_date = fields.Date(string='Test Date', required=True)
    test_type = fields.Selection([
        ('blood', 'Blood Test'),
        ('urine', 'Urine Test'),
        ('xray', 'X-Ray'),
        ('other', 'Other')
    ], string='Test Type')
    result = fields.Text(string='Result')
    notes = fields.Text(string='Notes')
