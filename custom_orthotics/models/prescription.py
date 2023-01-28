# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import time


class Prescription(models.Model):
    _name = 'custom_orthotics.prescription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'prescription_id'
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'date_hold': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')
    }

    prescription_id = fields.Char(string='ID', required=True, copy=False, readonly=True,
                                  index=True, default=lambda self: _('New'))
    date = fields.Datetime(
        string='Date', required=True)
    date_start = fields.Datetime(
        string='Date Start', required=True)
    date_end = fields.Datetime(
        string='Date End')
    date_hold = fields.Datetime(
        string='Hold Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('hold', 'On Hold'),
    ], string='Status', default='draft')
    description = fields.Text(string='Description')

    # Owner
    owner = fields.Many2one(
        'custom_orthotics.doctor', required=True)
    owner_id = fields.Integer(related='owner.id', string='Doctor')

    # Patient
    patient = fields.Many2one('custom_orthotics.patient', required=True,
                              domain="[('owner', '=', owner)]")
    patient_rec_name = fields.Char(
        related='patient.rec_name', string='Patient Recname')
    patient_id = fields.Integer(related='patient.id', string='Patient')
    patient_name = fields.Char(related='patient.name', string='Patient')

    # Item
    item_product = fields.Many2one(
        'custom_orthotics.item', string='Product', required=True, domain="[('item_type', '=', 'product')]")

    item_service = fields.Many2many(
        'custom_orthotics.item', string='Service', domain="[('item_type', '=', 'service')]")

    foot_selection = fields.Selection(
        [('left_only', 'Left Only'), ('right_only', 'Right Only'),
         ('bilateral', 'Bilateral')], default='bilateral')

    # Practice
    # practice = fields.Many2one(
    #     'custom_orthotics.practice', required=True, domain="[('item_service', '=', item_service)]")
    practice = fields.Many2one('custom_orthotics.practice', required=True)
    practice_id = fields.Integer(related='practice.id', string='Practice')
    practice_name = fields.Char(related='practice.name', string='Practice')

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

    def action_hold(self):
        for rec in self:
            rec.state = 'hold'
