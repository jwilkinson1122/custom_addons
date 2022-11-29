# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class Patient(models.Model):

    _name = 'pod.patient'
    _description = 'pod.patient'
    _rec_name = 'patient_id'

    @api.onchange('patient_id')
    def _onchange_patient(self):
        '''
        The purpose of the method is to define a domain for the available
        purchase orders.
        '''
        address_id = self.patient_id
        self.partner_address_id = address_id

    @api.depends('date_of_birth')
    def onchange_age(self):
        for rec in self:
            if rec.date_of_birth:
                d1 = rec.date_of_birth
                d2 = datetime.today().date()
                rd = relativedelta(d2, d1)
                rec.age = str(rd.years) + "y" + " " + \
                    str(rd.months) + "m" + " " + str(rd.days) + "d"
            else:
                rec.age = "No Date Of Birth!!"

    patient_id = fields.Many2one('res.partner', domain=[(
        'is_patient', '=', True)], string="Patient", required=True)
    name = fields.Char(string='ID', readonly=True)
    last_name = fields.Char('Last Name')
    date_of_birth = fields.Date(string="Date of Birth")
    gender = fields.Selection([('m', 'Male'), ('f', 'Female')], string="Sex")
    age = fields.Char(compute=onchange_age, string="Patient Age", store=True)
    partner_address_id = fields.Many2one('res.partner', string="Address", )
    street = fields.Char(related='patient_id.street', readonly=False)
    street2 = fields.Char(related='patient_id.street2', readonly=False)
    zip_code = fields.Char(related='patient_id.zip', readonly=False)
    city = fields.Char(related='patient_id.city', readonly=False)
    state_id = fields.Many2one(
        "res.country.state", related='patient_id.state_id', readonly=False)
    country_id = fields.Many2one(
        'res.country', related='patient_id.country_id', readonly=False)
    primary_doctor_id = fields.Many2one(
        'pod.doctor', string="Primary Care Doctor")
    practice_id = fields.Many2one(
        'pod.practice', string="Practice")
    # practice_id = fields.Many2one(
    #     comodel_name='pod.practice', string='Practice')
    patient_status = fields.Char(
        string="Hospitalization Status", readonly=True)
    lastname = fields.Char('Last Name')

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)

    @api.model
    def create(self, val):

        if val.get('date_of_birth'):
            dt = val.get('date_of_birth')
            d1 = datetime.strptime(str(dt), "%Y-%m-%d").date()
            d2 = datetime.today().date()
            rd = relativedelta(d2, d1)
            age = str(rd.years) + "y" + " " + str(rd.months) + \
                "m" + " " + str(rd.days) + "d"
            val.update({'age': age})

        patient_id = self.env['ir.sequence'].next_by_code('pod.patient')
        if patient_id:
            val.update({
                'name': patient_id,
            })
        result = super(Patient, self).create(val)
        return result

    def copy(self, default=None):
        for rec in self:
            raise UserError(_('You Can Not Duplicate Patient.'))

# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
