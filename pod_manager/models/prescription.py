from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class PracticePrescription(models.Model):
    _name = 'pod.manager.prescription'
    _description = 'Prescriptions'
    _order = "id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Prescription Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    patient_id = fields.Many2one(
        "pod.manager.patient", string='Patient Name', required=True)
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
    prescription_date = fields.Datetime(
        string='Prescription Date', default=fields.datetime.now(), tracking=True)
    requested_date = fields.Datetime(
        string='Requested Date', required=True, tracking=True)
    prescription_device_ids = fields.One2many("pod.manager.practice.prescription.device",
                                              "prescription_device_id", string="Prescription Device")
    appointed_doctor_id = fields.Many2one(
        "pod.manager.doctor", string="Doctor name", required=True)
    prescription_medical_test_ids = fields.Many2many("pod.manager.medical.test", "medical_test_ids",
                                                     string="Medical tests")

    @api.constrains('prescription_date', 'requested_date')
    def _check_date_validation(self):
        for record in self:
            if record.requested_date < record.prescription_date:
                raise ValidationError(
                    'Checkup date should not be previous date.')

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
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'pod.manager.prescription') or _('New')

        res = super(PracticePrescription, self).create(vals)
        return res

    @api.onchange('patient_id')
    def _change_prescription_note(self):
        if self.patient_id:
            if not self.note:
                self.note = "New prescription"
        else:
            self.note = ""


# for device record in patient prescription
class PracticePrescriptionDevice(models.Model):
    _name = "pod.manager.practice.prescription.device"
    _description = "Prescription Prescription Device"

    name = fields.Char(string="Device", required=True)
    quantity = fields.Integer(string="Quantity")
    prescription_device_id = fields.Many2one(
        "pod.manager.prescription", string="Prescription device")
