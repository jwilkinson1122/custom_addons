# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import time

# model_pod_clinic_prescription


class Prescription(models.Model):
    _name = 'pod_clinic.prescription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'prescription_id'
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    prescription_id = fields.Char(string='ID', required=True, copy=False, readonly=True,
                                  index=True, default=lambda self: _('New'))
    date = fields.Datetime(
        string='Date', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    ], string='Status', default='draft')
    description = fields.Text(string='Description')

    # Owner
    owner = fields.Many2one(
        'pod_clinic.practice', required=True)
    owner_id = fields.Integer(related='owner.id')

    # Patient
    patient = fields.Many2one('pod_clinic.patient', required=True,
                              domain="[('owner', '=', owner)]")
    patient_rec_name = fields.Char(
        related='patient.rec_name', string='Patient Recname')
    patient_id = fields.Integer(related='patient.id', string='Patient')
    patient_name = fields.Char(related='patient.name', string='Patient')

    # Item
    item_service = fields.Many2one(
        'pod_clinic.item', string='Accommodation', required=True, domain="[('item_type', '=', 'service')]")

    # Doctor
    doctor = fields.Many2one(
        'pod_clinic.doctor', required=True, domain="[('item_service', '=', item_service)]")
    doctor_id = fields.Integer(related='doctor.id', string='Doctor')
    doctor_name = fields.Char(related='doctor.name', string='Doctor')

    @api.model
    def create(self, vals):
        if vals.get('prescription_id', _('New')) == _('New'):
            vals['prescription_id'] = self.env['ir.sequence'].next_by_code(
                'patient_prescription.seq') or _('New')
        result = super(Prescription, self).create(vals)
        return result

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_cancel(self):
        for rec in self:
            rec.state = 'canceled'
