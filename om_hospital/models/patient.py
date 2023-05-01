# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import re
from datetime import date
from dateutil import relativedelta


class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hospital Patient Model"
    # order depends on multiple fields
    _order = "name,age desc"

    name = fields.Char(string='Name', required=True, tracking=True)
    date_of_birth = fields.Date(string='Date Of Birth')
    age = fields.Integer(string='Age', compute='_compute_age', inverse='_inverse_compute_age',  tracking=True)
    # computed field
    prescriptions_count = fields.Integer(string='Prescriptions Count', compute='_compute_prescriptions_count')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], required=True, tracking=True)
    note = fields.Text(string='Description', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'cancelled'),
    ], default='draft', string="Status", tracking=True)

    # Many2one Relation
    responsible_id = fields.Many2one('res.partner', string="Responsible", tracking=True)
    # one2many Relation
    prescription_ids = fields.One2many('hospital.prescription', 'patient_id', string="Prescriptions")
    reference = fields.Char(string='Patient Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    image = fields.Binary(string="Patient Image")
    email = fields.Char(string="Email", required=True)

    # computed method
    def _compute_prescriptions_count(self):
        # Singleton Error => solve for rec in self:
        for rec in self:
            num = rec.env['hospital.prescription'].search_count([('patient_id', '=', rec.id)])
            rec.prescriptions_count = num
            print(rec.env['hospital.prescription'])

    # buttons functions
    def action_confirm(self):
        if self.state != 'confirm':
            self.state = 'confirm'
        else:
            raise ValidationError(_("Sorry, %s has already Confirm state!" % self.reference))

    def action_cancel(self):
        if self.state != 'cancel':
            self.state = 'cancel'
        else:
            raise ValidationError(_("Sorry, %s has already Cancel state!" % self.reference))

    def action_done(self):
        if self.state != 'done':
            self.state = 'done'
        else:
            raise ValidationError(_("Sorry, %s has already done state!" % self.reference))

    # override create function
    @api.model
    def create(self, vals):
        if not vals.get('note'):
            vals['note'] = "New Patient"
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('patient.no') or _('New')
        return super(HospitalPatient, self).create(vals)

    # override default value function => called when we add default='value' attr.
    # when we override it we can add all default values in it
    @api.model
    def default_get(self, fields):
        vals = super(HospitalPatient, self).default_get(fields)
        vals['gender'] = 'female'
        return vals

    # override delete function
    def unlink(self):
        if self.state == 'done':
            raise ValidationError(_("Sorry, You can not delete %s that has a DONE status!" % self.reference))
        return super(HospitalPatient, self).unlink()

    # add constrains to field
    @api.constrains('email')
    def check_email_value(self):
        for rec in self:
            # unique
            patient = self.env['hospital.patient'].search([('email', '=', rec.email), ('id', '!=', rec.id)])
            # match email format
            if not re.match('(\w+[.|\w])*@(\w+[.])*\w+', self.email):
                raise UserError("Email not valid.")
            if patient:
                raise UserError("Email already exist.")

    # override name get method _rec_name
    def name_get(self):
        result = []
        for account in self:
            name = '[' + account.reference + '] ' + account.name
            result.append((account.id, name))
        return result

    # action to smart bottom prescriptions
    def action_open_prescription(self):
        action = self.env['ir.actions.actions']._for_xml_id('om_hospital.prescriptions_action')
        # condition to view only this patient's prescriptions
        action['domain'] = [('patient_id', '=', self.id)]
        '''to set default value for patient_id 
        when create new prescription by click on create in patient's prescriptions view'''
        action['context'] = {'default_patient_id': self.id}
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