# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HospitalPatient(models.Model):
    _name = "podiatry.patient"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Podiatry Patient"
    _order = "id desc"

    @api.model
    def default_get(self, fields):
        res = super(HospitalPatient, self).default_get(fields)
        res['note'] = 'NEW Patient Created'
        return res

    name = fields.Char(string='Name', required=True, tracking=True)
    reference = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))
    age = fields.Integer(string='Age', tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], required=True, default='male', tracking=True)
    note = fields.Text(string='Description')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'),
                              ('done', 'Done'), ('cancel', 'Cancelled')], default='draft',
                             string="Status", tracking=True)
    responsible_id = fields.Many2one('res.partner', string="Responsible")

    prescription_count = fields.Integer(
        string='E-Prescription Count', compute='_compute_prescription_count')

    image = fields.Binary(string="Patient Image")

    prescription_ids = fields.One2many(
        'podiatry.eprescription', 'patient_id', string="Prescriptions")

    def _compute_prescription_count(self):
        for rec in self:
            prescription_count = self.env['podiatry.eprescription'].search_count(
                [('patient_id', '=', rec.id)])
            rec.prescription_count = prescription_count

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.model
    def create(self, vals):
        if not vals.get('note'):
            vals['note'] = 'New Patient'
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'podiatry.patient') or _('New')
        res = super(HospitalPatient, self).create(vals)
        return res

    @api.constrains('name')
    def check_name(self):
        for rec in self:
            patients = self.env['podiatry.patient'].search(
                [('name', '=', rec.name), ('id', '!=', rec.id)])
            if patients:
                raise ValidationError(_("Name %s Already Exists" % rec.name))

    @api.constrains('age')
    def check_age(self):
        for rec in self:
            if rec.age == 0:
                raise ValidationError(_("Age Cannot Be Zero .. !"))

    def name_get(self):
        result = []
        for rec in self:
            name = '[' + rec.reference + '] ' + rec.name
            result.append((rec.id, name))
        return result

    def action_open_prescriptions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'podiatry.eprescription',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current',
        }
