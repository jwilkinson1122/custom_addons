# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class pod_patient(models.Model):

    _name = 'pod.patient'
    _description = 'Patient'
    _rec_name = 'pod_patient_id'

    @api.onchange('pod_patient_id')
    def _onchange_patient(self):
        '''
        The purpose of the method is to define a domain for the available
        purchase orders.
        '''
        address_id = self.pod_patient_id
        self.partner_address_id = address_id

    def print_report(self):
        return self.env.ref('pod_module.report_print_pod_patient_info').report_action(self)

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

    pod_patient_id = fields.Many2one('res.partner', domain=[(
        'is_patient', '=', True)], string="Patient", required=True)
    name = fields.Char(string='ID', readonly=True)
    last_name = fields.Char('Last Name')
    lastName = fields.Char('Last Name')
    first_name = fields.Chard('First Name')
    firstName = fields.Chard('First Name')
    gender = fields.Selection(
        [('m', 'Male'), ('f', 'Female')], string="Gender")
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Char(compute=onchange_age, string="Patient Age", store=True)
    general_info = fields.Text(string="Patient - General Information")
    # photo = fields.Binary(string="Picture")

    # models and photo objects
    left_photo = fields.Binary(string='Left Photo')
    right_photo = fields.Binary(string='Right Photo')
    # left_model = fields.Binary(string='Left Model')
    # right_model = fields.Binary(string='Right Model')

    partner_address_id = fields.Many2one('res.partner', string="Address", )
    primary_doctor_id = fields.Many2one('pod.doctor', string="Primary Doctor")
    pod_patient_condition_ids = fields.One2many(
        'pod.patient.condition', 'pod_patient_id')
    general_info = fields.Text(string="Info")
    notes = fields.Text(string="Extra info")
    report_date = fields.Date('Date', default=datetime.today().date())
    device_ids = fields.One2many(
        'pod.patient.device1', 'pod_patient_device_id')
    # notes = fields.Text('Notes')

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('pod.patient')
        vals['name'] = sequence or _('New')
        result = super(pod_patient, self).create(vals)
        return result
    # @api.model
    # def create(self,val):
    #     appointment = self._context.get('appointment_id')
    #     res_partner_obj = self.env['res.partner']
    #     if appointment:
    #         val_1 = {'name': self.env['res.partner'].browse(val['pod_patient_id']).name}
    #         patient= res_partner_obj.create(val_1)
    #         val.update({'pod_patient_id': patient.id})
    #     if val.get('date_of_birth'):
    #         dt = val.get('date_of_birth')
    #         d1 = datetime.strptime(str(dt), "%Y-%m-%d").date()
    #         d2 = datetime.today().date()
    #         rd = relativedelta(d2, d1)
    #         age = str(rd.years) + "y" +" "+ str(rd.months) + "m" +" "+ str(rd.days) + "d"
    #         val.update({'age':age} )

    #     pod_patient_id  = self.env['ir.sequence'].next_by_code('pod.patient')
    #     if pod_patient_id:
    #         val.update({
    #                     'name':pod_patient_id,
    #                    })
    #     result = super(pod_patient, self).create(val)
    #     return result

# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
