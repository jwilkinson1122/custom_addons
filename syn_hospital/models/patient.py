# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class om_hospital(models.Model):
#     _name = 'om_hospital.om_hospital'
#     _description = 'om_hospital.om_hospital'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HospitalPatient(models.Model):
    _name = 'syn.hospital.patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Syn Hospital Patient'


    name = fields.Char(string="Name",tracking=True)
    ref = fields.Char(string="Reference")
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Integer(string="Age", compute='_compute_age')
    gender = fields.Selection([('male','Male'),('female','Female')], string="Gender")
    active = fields.Boolean(string="Active",default=True)
    image = fields.Image(string="Image")
    senior_citizen = fields.Boolean(string="Senior Citizen")
    color = fields.Integer(string="Color")
    color_2 = fields.Char(string="Color")
    appointment_count = fields.Integer(string="Appointment Count", compute="_compute_appointment_count", store=True)
    appointment_ids = fields.One2many('syn.hospital.appointment','patient_id',string="Appointment")

    parent = fields.Char(string="Parent")
    martial_status = fields.Selection([('married','Married'),('single','Single')], string="Marital Status")
    partner = fields.Char(string="Partner Name")

    # _sql_constraints = [
    #     ('unique_patient_name', 'unique (name)', 'name must be unique')
    # ]

    # this function will trigger when appointment create (for updating count)
    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for rec in self:
            rec.appointment_count = self.env['syn.hospital.appointment'].search_count([('patient_id','=',rec.id)])

    @api.model
    def create(self,vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('syn.hospital.patient')
        return super(HospitalPatient,self).create(vals)

    @api.ondelete(at_uninstall=False)
    def _check_apt(self):
        for rec in self:
            if rec.appointment_ids:
                raise ValidationError(_('You can not delete patient with appointments !'))

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            today = date.today()
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year
                if rec.age >= 60:
                    rec.senior_citizen = True
                else:
                    rec.senior_citizen = False
            else:
                rec.age = 0

    # @api.constrains('date_of_birth','name')
    @api.constrains('date_of_birth')
    def check_birth_of_date(self):
        for rec in self:
            if rec.date_of_birth and rec.date_of_birth > fields.Date.today():
                raise ValidationError(_('entered date of birth is not acceptable !'))