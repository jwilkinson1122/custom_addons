# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date
from dateutil import relativedelta


class HospitalDoctor(models.Model):
    _name = "hospital.doctor"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hospital Doctor Model"

    name = fields.Char(string='Name', required=True, tracking=True)
    date_of_birth = fields.Date(string='Date Of Birth')
    age = fields.Integer(string='Age', compute='_compute_age', inverse='_inverse_compute_age', tracking=True)

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], required=True, tracking=True)
    note = fields.Text(string='Description', tracking=True)
    state = fields.Selection([
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('not_available', 'Not Available'),

    ], default='not_available', string="Status", tracking=True)

    reference = fields.Char(string='Doctor Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    image = fields.Binary(string="Patient Image", copy=0)

    prescriptions_count = fields.Integer(string='Prescriptions Count', compute='_compute_prescriptions_count')

    active = fields.Boolean(default=True)

    # buttons functions
    def action_available(self):
        if self.state != 'available':
            self.state = 'available'
        else:
            raise ValidationError(_("Sorry, %s has already available state!" % self.reference))

    def action_busy(self):
        if self.state != 'busy':
            self.state = 'busy'
        else:
            raise ValidationError(_("Sorry, %s has already busy state!" % self.reference))

    # override create function
    @api.model
    def create(self, vals):
        if not vals.get('note'):
            vals['note'] = "No Description"
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('doctor.no') or _('New')
        return super(HospitalDoctor, self).create(vals)

    # override copy(duplicate) method
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (Copy)") % self.name
            # if you want to erase value (do not copy it )
            # there is two methods => in field you can add this attribute copy="0" look at image or this method
            default['age'] = ""
        return super(HospitalDoctor, self).copy(default=default)

    # computed method
    def _compute_prescriptions_count(self):
        # Singleton Error => solve for rec in self:
        for rec in self:
            num = rec.env['hospital.prescription'].search_count([('doctor_id', '=', rec.id)])
            rec.prescriptions_count = num
            print(rec.env['hospital.prescription'])

    # action to smart bottom prescriptions
    def action_open_prescription(self):
        action = self.env['ir.actions.actions']._for_xml_id('om_hospital.prescriptions_action')
        # condition
        action['domain'] = [('doctor_id', '=', self.id)]
        '''to set default value for doctor_id 
                when create new prescription by click on create in doctor's prescriptions view'''
        action['context'] = {'default_doctor_id': self.id}
        return action

    @api.constrains('date_of_birth')
    def _check_date_of_birth(self):
        for rec in self:
            if rec.date_of_birth and rec.date_of_birth > fields.Date.today():
                raise ValidationError(_("The entered date of birth is not acceptable !"))

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            today = date.today()
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year
            else:
                rec.age = 0

    @api.depends('age')
    def _inverse_compute_age(self):
        today = date.today()
        for rec in self:
            rec.date_of_birth = today - relativedelta.relativedelta(years=rec.age)








