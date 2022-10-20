from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Prescription(models.Model):
    _name = 'podiatry.prescription'
    _description = 'Prescription'
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

    practitioner_phone = fields.Char(
        string='Phone', related='practitioner_id.phone')
    practitioner_email = fields.Char(
        string='Email', related='practitioner_id.email')

    patient_id = fields.Many2one(
        comodel_name='podiatry.patient',
        string='Patient')

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], related='patient_id.gender')

    patient_phone = fields.Char(string='Phone', related='patient_id.phone')
    patient_email = fields.Char(string='Email', related='patient_id.email')
    # patient_age = fields.Integer(string='Age', related='patient_id.age')

    description = fields.Text(string='Description')

    diagnosis_id = fields.Many2one(
        comodel_name='podiatry.patient.diagnosis',
        string='diagnosis')

    prescription_date = fields.Datetime(
        'Prescription Date', default=fields.Datetime.now)

    user_id = fields.Many2one(
        'res.users', 'Login User', readonly=True, default=lambda self: self.env.user)

    attachment_ids = fields.Many2many('ir.attachment', 'prescription_ir_attachments_rel',
                                      'manager_id', 'attachment_id', string="Attachments",
                                      help="Images/attachments before prescription")

    inv_state = fields.Selection(
        [('invoiced', 'To Invoiced'), ('tobe', 'To Be Invoiced')], 'Invoice Status')

    no_invoice = fields.Boolean('Invoice exempt')

    inv_id = fields.Many2one('account.invoice', 'Invoice')

    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                              ('done', 'Done'), ('cancel', 'Cancelled')], default='draft',
                             string="Status", tracking=True)

    prescription_date = fields.Date(string="Date", tracking=True)

    completed_date = fields.Datetime(string="Completed Date")

    prescription_count = fields.Integer(
        string='Prescription Count', compute='_compute_prescription_count')

    prescription = fields.Text(string="Prescription")

    prescription_ids = fields.One2many(
        'podiatry.prescription', 'patient_id', string="Prescriptions")

    prescription_line_ids = fields.One2many(
        'podiatry.prescription.line', 'prescription_id', 'Prescription Line')

    # line_ids = fields.One2many(
    #     "library.checkout.line",
    #     "checkout_id",
    #     string="Borrowed Books",
    # )

    def _compute_prescription_count(self):
        for rec in self:
            prescription_count = self.env['podiatry.prescription'].search_count(
                [('patient_id', '=', rec.id)])
            rec.prescription_count = prescription_count

    invoice_done = fields.Boolean('Invoice Done')

    notes = fields.Text('Prescription Note')

    is_invoiced = fields.Boolean(copy=False, default=False)

    is_shipped = fields.Boolean(default=False, copy=False)

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
                'podiatry.prescription') or _('New')
        res = super(Prescription, self).create(vals)
        return res

    def prescription_report(self):
        return self.env.ref('podiatry.report_print_prescription').report_action(self)

    # @api.onchange('patient_id', 'practitioner_id', 'date')
    # def _onchange_name(self):
    #     self.name = f'{self.patient_id.name} | {self.practitioner_id.name} ({self.date})'

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            if self.patient_id.gender:
                self.gender = self.patient_id.gender
            if self.patient_id.notes:
                self.notes = self.patient_id.notes
        else:
            self.gender = ''
            self.notes = ''
    # @api.onchange('patient_id')
    # def _change_prescription_notes(self):
    #     if self.patient_id:
    #         if not self.notes:
    #             self.notes = "New prescription"
    #     else:
    #         self.notes = ""

    def unlink(self):
        if self.state == 'done':
            raise ValidationError(
                _("You Cannot Delete %s as it is in Done State" % self.name))
        return super(Prescription, self).unlink()

    def action_url(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'https://nwpodiatric.com' % self.prescription,
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# for device record in patient prescription
# class PrescriptionDevice(models.Model):
#     _name = "podiatry.prescription.device"
#     _description = "Prescription Device"

#     name = fields.Char(string="Device", required=True)
#     quantity = fields.Integer(string="Quantity")
#     prescription_device_id = fields.Many2one(
#         "podiatry.prescription", string="Prescription device")
