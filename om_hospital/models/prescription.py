# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HospitalPrescription(models.Model):
    _name = "podiatry.eprescription"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Podiatry E-Prescription"
    _order = "doctor_id,name,age"

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    patient_id = fields.Many2one(
        'podiatry.patient', string="Patient", required=True)
    age = fields.Integer(
        string='Age', related='patient_id.age', tracking=True, store=True)
    doctor_id = fields.Many2one(
        'podiatry.doctor', string="Doctor", required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string="Gender")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                              ('done', 'Done'), ('cancel', 'Cancelled')], default='draft',
                             string="Status", tracking=True)
    note = fields.Text(string='Description')
    date_prescription = fields.Date(string="Date")
    date_checkup = fields.Datetime(string="Check Up Time")
    eprescription = fields.Text(string="E-Prescription")
    prescription_line_ids = fields.One2many('eprescription.eprescription.lines', 'prescription_id',
                                            string="E-Prescription Lines")

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
                'podiatry.eprescription') or _('New')
        res = super(HospitalPrescription, self).create(vals)
        return res

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
        return super(HospitalPrescription, self).unlink()

    def action_url(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'https://apps.odoo.com/apps/modules/14.0/%s/' % self.eprescription,
        }


class PrescriptionPrescriptionLines(models.Model):
    _name = "eprescription.eprescription.lines"
    _description = "E-Prescription E-Prescription Lines"

    name = fields.Char(string="Medicine", required=True)
    qty = fields.Integer(string="Quantity")
    prescription_id = fields.Many2one(
        'podiatry.eprescription', string="E-Prescription")
