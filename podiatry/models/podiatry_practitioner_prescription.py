from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PractitionerPrescription(models.Model):
    _name = 'podiatry.practitioner.prescription'
    _description = 'Practitioner Prescription'
    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    # readonly = True
    active = fields.Boolean(default=True)
    color = fields.Integer()
    date = fields.Date()
    time = fields.Datetime()

    practice_id = fields.Many2one(
        comodel_name='podiatry.practice',
        string='Practice')

    practitioner_id = fields.Many2one(
        comodel_name='podiatry.practitioner',
        string='Practitioner')

    patient_id = fields.Many2one(
        comodel_name='podiatry.patient',
        string='Patient')

    description = fields.Text(string='Description')

    diagnosis_id = fields.Many2one(
        comodel_name='podiatry.patient.diagnosis',
        string='diagnosis')

    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                              ('done', 'Done'), ('cancel', 'Cancelled')], default='draft',
                             string="Status", tracking=True)
    note = fields.Text(string='Description')
    prescription_date = fields.Date(string="Date")
    completed_date = fields.Datetime(string="Created Date")
    prescription = fields.Text(string="Prescription")
    prescription_line_ids = fields.One2many('podiatry.practitioner.prescription.lines', 'prescription_id',
                                            string="Prescription Lines")

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], related='patient_id.gender')

    def action_confirm(self):
        self.state = 'confirm'

    def action_done(self):
        self.state = 'done'

    def action_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        self.state = 'cancel'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'hospital.prescription') or _('New')
        res = super(PractitionerPrescription, self).create(vals)
        return res

    @api.onchange('patient_id', 'practitioner_id', 'date')
    def _onchange_name(self):
        self.name = f'{self.patient_id.name} | {self.practitioner_id.name} ({self.date})'

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            if self.patient_id.gender:
                self.gender = self.patient_id.gender
            if self.patient_id.note:
                self.note = self.patient_id.note
        else:
            self.gender = ''
            self.note = ''

    def unlink(self):
        if self.state == 'done':
            raise ValidationError(
                _("You Cannot Delete %s as it is in Done State" % self.name))
        return super(PractitionerPrescription, self).unlink()

    def action_url(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'https://nwpodiatric.com' % self.prescription,
        }


class PractitionerPrescriptionLines(models.Model):

    _name = 'podiatry.practitioner.prescription.lines'
    _description = "Prescription Lines"
    name = fields.Char(string="Device", required=True)

    qty = fields.Integer(string="Quantity")
    prescription_id = fields.Many2one(
        'podiatry.practitioner.prescription', string="Prescription")
