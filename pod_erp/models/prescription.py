from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class PracticePrescription(models.Model):
    _name = 'pod_erp.prescription'
    _description = 'Prescriptions'
    _order = "id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Prescription Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    patient_id = fields.Many2one("pod_erp.patient", string='Patient Name', required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], related='patient_id.gender')
    phone = fields.Char(string='Phone', related='patient_id.phone')
    email = fields.Char(string='Email', related='patient_id.email')
    age = fields.Integer(string='Age', related='patient_id.age')
    description = fields.Text()
    note = fields.Text()
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Canceled')
    ], default='draft', required=True, tracking=True)
    prescription_date = fields.Datetime(string='Prescription Date', default=fields.datetime.now(), tracking=True)
    checkup_date = fields.Datetime(string='Checkup Date', required=True, tracking=True)
    prescription_medicine_ids = fields.One2many("pod_erp.prescription.prescription.medicine",
                                                "prescription_medicine_id", string="Prescription Medicine")
    appointed_doctor_id = fields.Many2one("res.partner", string="Doctor name", required=True)
    prescription_medical_test_ids = fields.Many2many("pod_erp.medicaltest", "medical_test_ids",
                                                     string="Medical tests")

    @api.constrains('prescription_date', 'checkup_date')
    def _check_date_validation(self):
        for record in self:
            if record.checkup_date < record.prescription_date:
                raise ValidationError('Checkup date should not be previous date.')

    # changing the status
    def action_status_draft(self):
        self.status = 'draft'

    def action_status_confirm(self):
        self.status = 'confirm'

    def action_status_done(self):
        self.status = 'done'

    def action_status_cancel(self):
        self.status = 'cancel'

    @api.model
    def create(self, vals):
        if not vals['description']:
            vals['description'] = "Enter the description here"
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('pod_erp.prescription') or _('New')

        res = super(PracticePrescription, self).create(vals)
        return res

    @api.onchange('patient_id')
    def _change_prescription_note(self):
        if self.patient_id:
            if not self.note:
                self.note = "New prescription"
        else:
            self.note = ""


# for medicine record in patient prescription
class PrescriptionPrescriptionMedicine(models.Model):
    _name = "pod_erp.prescription.prescription.medicine"
    _description = "Prescription Prescription Medicine"

    name = fields.Char(string="Medicine", required=True)
    quantity = fields.Integer(string="Quantity")
    prescription_medicine_id = fields.Many2one("pod_erp.prescription", string="Prescription medicine")
