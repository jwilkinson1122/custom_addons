
from odoo import api, fields, models, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class Patient(models.Model):

    _name = 'podiatry.patient'
    _description = 'Medical Patient'
    _inherits = {
        'res.partner': 'partner_id',
    }
    _rec_name = 'partner_id'

    @api.model
    def _get_sequence_code(self):
        return 'podiatry.patient'

    @api.onchange('partner_id')
    def _onchange_patient(self):
        '''
        The purpose of the method is to define a domain for the available
        purchase orders.
        '''
        address_id = self.partner_id
        self.partner_address_id = address_id

    def print_report(self):
        return self.env.ref('podiatry_erp.report_print_patient_card').report_action(self)

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
    lastname = fields.Char('Last Name')
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Char(compute=onchange_age, string="Patient Age", store=True)
    partner_address_id = fields.Many2one('res.partner', string="Address", )
    primary_doctor_id = fields.Many2one(
        'podiatry.doctor', string="Primary Doctor")
    patient_status = fields.Char(
        string="Status", readonly=True)
    general_info = fields.Text(string="Info")
    notes = fields.Text(string="Extra info")

    prescription_ids = fields.One2many(
        'podiatry.prescription', 'patient_id', string='Prescriptions')
    report_date = fields.Date('Date', default=datetime.today().date())
    # device_ids = fields.One2many(
    #     'podiatry.patient.device1', 'podiatry_patient_device_id')

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)

    @api.model
    def create(self, val):
        prescription = self._context.get('prescription_id')
        res_partner_obj = self.env['res.partner']
        if prescription:
            val_1 = {'name': self.env['res.partner'].browse(
                val['patient_id']).name}
            patient = res_partner_obj.create(val_1)
            val.update({'patient_id': patient.id})
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
        result = super(Patient, self).create(val)
        return result

# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
