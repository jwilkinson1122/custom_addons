# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import time


class Appointment(models.Model):
    _name = 'pet_clinic.appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'appointment_id'
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

    appointment_id = fields.Char(string='ID', required=True, copy=False, readonly=True,
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
        'pet_clinic.client', required=True)
    owner_id = fields.Integer(related='owner.id')

    # Pet
    pet = fields.Many2one('pet_clinic.pet', required=True,
                          domain="[('owner', '=', owner)]")
    pet_rec_name = fields.Char(related='pet.rec_name', string='Pet Recname')
    pet_id = fields.Integer(related='pet.id', string='Pet')
    pet_name = fields.Char(related='pet.name', string='Pet')

    # Item
    item_service = fields.Many2one(
        'pet_clinic.item', string='Service', required=True, domain="[('item_type', '=', 'service')]")

    # Doctor
    doctor = fields.Many2one(
        'pet_clinic.doctor', required=True, domain="[('item_service', '=', item_service)]")
    doctor_id = fields.Integer(related='doctor.id', string='Doctor')
    doctor_name = fields.Char(related='doctor.name', string='Doctor')

    @api.model
    def create(self, vals):
        if vals.get('appointment_id', _('New')) == _('New'):
            vals['appointment_id'] = self.env['ir.sequence'].next_by_code(
                'pet_appointment.seq') or _('New')
        result = super(Appointment, self).create(vals)
        return result

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_cancel(self):
        for rec in self:
            rec.state = 'canceled'
