# -*- coding: utf-8 -*-

import base64
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource


class HospitalDoctors(models.Model):
    _inherit = 'res.partner'
    # _rec_name = 'partner_id'
    
    name = fields.Char(string="Doctor Name")
    
    status = fields.Selection([('active', 'Active'),
                               ('inactive', 'Inactive')],
                              string="Doctor Status", required=True)
    
    doctor_seq = fields.Char(string='Doctor No.', required=True,
                              copy=False,
                              readonly=True,
                              index=True,
                              default=lambda self: 'New')
    
    # partner_id = fields.Many2one('res.partner','Doctor',required=True)

    # is_doctor = fields.Selection(string='Designation',
    #                              selection=[('employee', 'Employee'), ('doctor', 'Doctor')],
    #                              default='doctor')
    patient_ids = fields.One2many('res.partner', 'doctor_id', string='Patients')
    hospital_id = fields.Many2one('res.partner',domain=[('is_hospital','=',True)],string='Hospital')
    pharmacy_id = fields.Many2one('hospital.pharmacy', string="Pharmacy", required=True)
    consultancy_charge = fields.Monetary(string="Consultancy Charge")
    consultancy_type = fields.Selection([('resident', 'Residential'),
                                         ('special', 'Specialist')],
                                        string="Consultancy Type")
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.user.company_id
                                  .currency_id.id,
                                  required=True)
    degrees = fields.Many2many('hospital.degree', string="Degrees")
    institute = fields.Many2many('hospital.institution',
                                 string="Institution Name")
    specialization = fields.Many2many('hospital.specialization',
                                      string="Specialization", help="Doctors specialization for an area")
    
    
    
    prescription_ids = fields.One2many('hospital.prescription', 'doctor_id', 'Prescription')
    pharmacy_ids = fields.One2many('hospital.pharmacy', 'doctor_id', 'Pharmacy')
    notes = fields.Html('Note', sanitize_style=True)
    
    def name_get(self):
        res = []
        for name in self:
            res.append((name.id, ("%s (%s)") % (name.name, name.doctor_seq)))
        return res

    @api.model
    def create(self, vals):
        if vals.get('doctor_seq', 'New') == 'New':
            vals['doctor_seq'] = self.env['ir.sequence'].next_by_code(
                'doctors.sequence') or 'New'
        result = super(HospitalDoctors, self).create(vals)
        return result


class DoctorSpecialty(models.Model):
    _name = 'doctor.specialty'
    _description = 'Medical Specialty'

    code = fields.Char(string='ID')
    name = fields.Char(string='Specialty', help='Name of the specialty', required=True)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]
