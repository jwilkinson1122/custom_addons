# -*- coding: utf-8 -*-
# Part of NWPL. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class medical_patient(models.Model):
    
    _name = 'medical.patient'
    _description = 'medical patient'
    _rec_name = 'patient_id'
    
    @api.onchange('patient_id')
    def _onchange_patient(self):
        '''
        The purpose of the method is to define a domain for the available
        purchase orders.
        '''
        address_id = self.patient_id
        self.partner_address_id = address_id

    def print_report(self):
        return self.env.ref('pod_hms.report_print_patient_card').report_action(self)

    @api.depends('date_of_birth')
    def onchange_age(self):
        for rec in self:
            if rec.date_of_birth:
                d1 = rec.date_of_birth
                d2 = datetime.today().date()
                rd = relativedelta(d2, d1)
                rec.age = str(rd.years) + "y" +" "+ str(rd.months) + "m" +" "+ str(rd.days) + "d"
            else:
                rec.age = "No Date Of Birth!!"
    
    partner_id = fields.Many2one('res.partner', string='Related Partner', ondelete='cascade',
                                 help='Partner-related data of the Patient')
    patient_id = fields.Many2one('res.partner',domain=[('is_patient','=',True)], required= True)
    name = fields.Char(string='Patient ID', readonly=True)
    last_name = fields.Char('Last Name')
    date_of_birth = fields.Date(string="Date of Birth")
    gender = fields.Selection(selection=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string="Gender")
    age = fields.Char(compute=onchange_age,string="Patient Age",store=True)
    patient_info = fields.Text(string="Patient Information")
    photo = fields.Binary(string="Picture")
    partner_address_id = fields.Many2one('res.partner', string="Address", )
    street = fields.Char(related='patient_id.street', readonly=False)
    street2 = fields.Char(related='patient_id.street2', readonly=False)
    zip_code = fields.Char(related='patient_id.zip', readonly=False)
    city = fields.Char(related='patient_id.city', readonly=False)
    state_id = fields.Many2one("res.country.state", related='patient_id.state_id', readonly=False)
    country_id = fields.Many2one('res.country', related='patient_id.country_id', readonly=False)
    
    practice_id = fields.Many2one(comodel_name='medical.practice', required=True, string="Practice")
    
    primary_care_practitioner_id = fields.Many2one('medical.practitioner', string="Primary Care Practitioner")
    
    prescription_ids = fields.One2many(
        comodel_name='medical.prescription.order',
        inverse_name='patient_id',
        string='Prescriptions')
    
    patient_status = fields.Char(string="Status",readonly=True)
    patient_condition_ids = fields.One2many('medical.patient.condition','patient_id')
    general_info = fields.Text(string="Info")
    lastname = fields.Char('Last Name')
    report_date = fields.Date('Date',default = datetime.today().date())
    device_ids = fields.One2many('medical.patient.device1','medical_patient_device_id')
    notes = fields.Text('Notes')
    active = fields.Boolean(string="Active", default=True)

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)
    
    prescription_count = fields.Integer(compute='get_prescription_count')

    def open_patient_prescriptions(self):
        for records in self:
            return {
                'name': _('Patient Prescription'),
                'view_type': 'form',
                'domain': [('patient_id', '=', records.id)],
                'res_model': 'medical.prescription.order',
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_patient': self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['medical.prescription.order'].search_count(
                [('patient_id', '=', records.id)])
            records.prescription_count = count

    def copy(self, default=None):
        for rec in self:
            raise UserError(_('You Can Not Duplicate Patient.' ))

# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
