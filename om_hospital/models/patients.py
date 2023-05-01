# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class sale_order_inherit(models.Model):
    
    _inherit = 'sale.order'

    patient_name = fields.Char(string = 'Patient Name')


class hospital_patient(models.Model):
    _name = 'hospital.patient'
    
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    _description = 'Hospital Patient'
    _rec_name = 'name_seq'


    @api.constrains('patient_age')
    def check_age(self):
        for rec in self:
            if rec.patient_age <= 5:
                raise ValidationError(_('The Age Must be Greater than 5'))
            

    
    @api.depends('patient_age')
    def set_age_group(self):
        for rec in self:
            if rec.patient_age:
                if rec.patient_age < 18:
                    rec.age_group = 'minor'
                else:
                    rec.age_group = 'major'




    
    def button_patient_appointment(self):
        #import pdb; pdb.set_trace()
        return {
            'name': _('Appointments'),
            'domain': [('patient_id','=',self.name_seq)],
            'view_type': 'form',
            'res_model': 'hospital.appointment',
            'view_id': False,
            'view_mode':'tree,form',
            'type': 'ir.actions.act_window',
        }


    def get_appointment_count(self):
        count = self.env['hospital.appointment'].search_count([('patient_id','=',self.name_seq)])
        self.appointment_count =count


    patient_name = fields.Char(string = 'Name', required=True, track_visibility='always')
    patient_age = fields.Integer(string = 'Age', 
    track_visibility='always'
    )
    notes = fields.Text(string='Notes')
    image = fields.Binary(string='Image')
    name = fields.Char(string='Test')
    name_seq = fields.Char(string='Patient ID', 
    required=True, copy=False, readonly = True, default= lambda self: _('New'))


    gender = fields.Selection(
        string='Gender',
        selection=[('male', 'Male'), ('female', 'Female')],
        default='male'        
        )
    age_group = fields.Selection(
        string='Age Group',
        selection=[('major', 'Major'), ('minor', 'Minor')],
        compute='set_age_group'
        )   

    appointment_count = fields.Integer( 
        string='Appointment', compute='get_appointment_count'
    )

        
    REQUISITION_STATE = [
            ('draft', 'Draft'),
            ('confirm', 'Confirm'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
            ]
    state = fields.Selection(REQUISITION_STATE,string='Status', readonly=True, index=True, copy=False, 
                                default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.patient.sequence') or _('New')
        result =  super(hospital_patient,self).create(vals)
        return result

