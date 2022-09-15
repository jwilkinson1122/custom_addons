# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class podiatry_patient(models.Model):

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
        return self.env.ref('pod_hms.report_print_patient_card').report_action(self)

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
    gender = fields.Selection(
        [('m', 'Male'), ('f', 'Female')], string="Gender")
    age = fields.Char(compute=onchange_age, string="Patient Age", store=True)
    critical_info = fields.Text(string="Patient Critical Information")
    photo = fields.Binary(string="Picture")
    blood_type = fields.Selection(
        [('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O')], string="Blood Type")
    rh = fields.Selection([('-+', '+'), ('--', '-')], string="Rh")
    marital_status = fields.Selection([('s', 'Single'), ('m', 'Married'), (
        'w', 'Widowed'), ('d', 'Divorced'), ('x', 'Seperated')], string='Marital Status')
    deceased = fields.Boolean(string='Deceased')
    date_of_death = fields.Datetime(string="Date of Death")
    cause_of_death = fields.Char(string='Cause of Death')
    receivable = fields.Float(string="Receivable", readonly=True)
    partner_address_id = fields.Many2one('res.partner', string="Address", )
    primary_care_practitioner_id = fields.Many2one(
        'podiatry.practitioner', string="Primary Care Practitioner")
    patient_status = fields.Char(
        string="Podiatryization Status", readonly=True)
    patient_condition_ids = fields.One2many(
        'podiatry.patient.condition', 'patient_id')
    patient_products_services_ids = fields.One2many(
        'podiatry.patient.products.services', 'patient_id')
    general_info = fields.Text(string="Info")

    rx_ids = fields.One2many('podiatry.patient.rx', 'patient_id')
    lastname = fields.Char('Last Name')
    report_date = fields.Date('Date', default=datetime.today().date())
    device_ids = fields.One2many(
        'podiatry.patient.device1', 'podiatry_patient_device_id')
    deaths_2nd_week = fields.Integer('Deceased after 2nd week')
    deaths_1st_week = fields.Integer('Deceased after 1st week')
    ses_notes = fields.Text('Notes')

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

        patient_id = self.env['ir.sequence'].next_by_code('podiatry.patient')
        if patient_id:
            val.update({
                'name': patient_id,
            })
        result = super(podiatry_patient, self).create(val)
        return result

# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
