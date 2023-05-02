# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

class patient(models.Model):
    
    _name = 'podiatry.patient'
    _description = 'podiatry patient'
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
        return self.env.ref('pod_erp.report_print_patient_card').report_action(self)

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

    patient_id = fields.Many2one('res.partner',domain=[('is_patient','=',True)],string="Patient", required= True)
    name = fields.Char(string='ID', readonly=True)
    last_name = fields.Char('Last Name')
    lastname = fields.Char('Last Name')
    date_of_birth = fields.Date(string="Date of Birth")
    gender = fields.Selection([('m', 'Male'),('f', 'Female')], string ="Gender")
    age = fields.Char(compute=onchange_age,string="Patient Age",store=True)
    photo = fields.Binary(string="Picture")
    partner_address_id = fields.Many2one('res.partner', string="Address", )
    street = fields.Char(related='patient_id.street', readonly=False)
    street2 = fields.Char(related='patient_id.street2', readonly=False)
    zip_code = fields.Char(related='patient_id.zip', readonly=False)
    city = fields.Char(related='patient_id.city', readonly=False)
    state_id = fields.Many2one("res.country.state", related='patient_id.state_id', readonly=False)
    country_id = fields.Many2one('res.country', related='patient_id.country_id', readonly=False)
    primary_care_physician_id = fields.Many2one('podiatry.physician', string="Primary Care Doctor")
    patient_status = fields.Char(string="Activity Status",readonly=True)
    patient_condition_ids = fields.One2many('podiatry.patient.condition','patient_id')
    prescription_ids = fields.One2many('podiatry.prescription.order','patient_id',string='Prescriptions')
    general_info = fields.Text(string="Info")
    report_date = fields.Date('Date',default = datetime.today().date())
    orthotic_ids = fields.One2many('podiatry.patient.orthotic1','patient_orthotic_id')
    notes = fields.Text('Notes')

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)

    @api.model
    def create(self,val):
        # appointment = self._context.get('appointment_id')
        # res_partner_obj = self.env['res.partner']
        # if appointment:
        #     val_1 = {'name': self.env['res.partner'].browse(val['patient_id']).name}
        #     patient= res_partner_obj.create(val_1)
        #     val.update({'patient_id': patient.id})
        if val.get('date_of_birth'):
            dt = val.get('date_of_birth')
            d1 = datetime.strptime(str(dt), "%Y-%m-%d").date()
            d2 = datetime.today().date()
            rd = relativedelta(d2, d1)
            age = str(rd.years) + "y" +" "+ str(rd.months) + "m" +" "+ str(rd.days) + "d"
            val.update({'age':age} )

        patient_id  = self.env['ir.sequence'].next_by_code('podiatry.patient')
        if patient_id:
            val.update({
                        'name':patient_id,
                       })
        result = super(patient, self).create(val)
        return result

    def copy(self, default=None):
        for rec in self:
            raise UserError(_('You Can Not Duplicate Patient.' ))

# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
