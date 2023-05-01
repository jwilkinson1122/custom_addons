# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class hospital_appointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'patient_id'
    _order = 'id desc'


    @api.model
    def create(self, vals):
        if vals.get('apmt_seq', _('New')) == _('New'):
            vals['apmt_seq'] = self.env['ir.sequence'].next_by_code('hospital.appointment.sequence') or _('New')
        result = super(hospital_appointment, self).create(vals)
        return result

    def _get_default_note(self):
        return "Default Note"

    apmt_seq = fields.Char(string = 'Appointment ID', required=True, copy=False, readonly=True,index = True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True) 
    patient_age = fields.Integer(string='Age', related = 'patient_id.patient_age')
    notes = fields.Text(string='Notes', default=_get_default_note)
    appointment_date = fields.Date(string='Appointment Date',required=True)




   
