# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HospitalPrescriptions(models.Model):
    _name = "hospital.prescription"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hospital Prescriptions Model"
    # order by field desc
    _order = "reference desc"
    _rec_name = 'reference'

    note = fields.Text(string='Description', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'cancelled'),
    ], default='draft', string="Status", tracking=True)
    # to test onchange method
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], related='patient_id.gender', required=True, tracking=True)
    # Many2one Relation
    patient_id = fields.Many2one('hospital.patient', string="Patient", required=True, tracking=True)
    doctor_id = fields.Many2one('hospital.doctor', string="Doctor", required=True, tracking=True)
    reference = fields.Char(string='prescription Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    date_prescription = fields.Date(string="Date", required=True, tracking=True)
    date_check = fields.Datetime(string="Check Up Time")
    # related fields
    age = fields.Integer(string='Age', related='patient_id.age')
    responsible_id = fields.Many2one('res.partner', string="Responsible", tracking=True,
                                     related='patient_id.responsible_id')
    medicine_ids = fields.One2many('hospital.prescription.medicine', 'prescription_id', string="Medicine")

    def action_confirm(self):
        for rec in self:
            if rec.state != 'confirm':
                rec.state = 'confirm'
            else:
                raise ValidationError(_("Sorry, %s has already confirm state!" % self.reference))

    def action_cancel(self):
        for rec in self:
            if rec.state != 'cancel':
                rec.state = 'cancel'
            else:
                raise ValidationError(_("Sorry, %s has already Cancel state!" % self.reference))

    def action_done(self):
        for rec in self:
            if rec.state != 'done':
                rec.state = 'done'
            else:
                raise ValidationError(_("Sorry, %s has already Done state!" % self.reference))

    # override create function
    @api.model
    def create(self, vals):
        if not vals.get('note'):
            vals['note'] = "New Patient"
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('prescription.no') or _('New')
        return super(HospitalPrescriptions, self).create(vals)

    # onchange function
    @api.onchange('patient_id', 'note')
    def onchange_patient_id(self):
        if self.patient_id:
            # check if there is a value in patient_id.gender => gender = patient_id.gender
            if self.patient_id.gender:
                self.gender = self.patient_id.gender
            # check if there is a value in patient_id.note => note = patient_id.note
            if self.patient_id.note:
                self.note = self.patient_id.note
        else:
            self.gender = ''
            self.note = ''

    # override delete function
    def unlink(self):
        if self.state == 'done':
            raise ValidationError(_("Sorry, You can not delete %s that has a DONE status!" % self.reference))
        return super(HospitalPrescriptions, self).unlink()

    def action_url(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': '/web',
        }



class HospitalPrescriptionsMedicine(models.Model):
    _name = "hospital.prescription.medicine"
    # order by field desc
    _order = "name desc"

    name = fields.Char(string="Name")
    quantity = fields.Integer(string="Quantity")
    prescription_id = fields.Many2one('hospital.prescription', string="Prescription")
