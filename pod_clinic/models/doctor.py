# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Doctor(models.Model):
    _name = 'pod_clinic.doctor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    doctor_id = fields.Char(string='ID', required=True, copy=False, readonly=True,
                            index=True, default=lambda self: _('New'))
    name = fields.Char(string='Name', required=True)
    image = fields.Binary(string='Image', attachment=True)
    active = fields.Boolean(string="Active", default=True, tracking=True)
    color = fields.Integer(string="Color Index (0-15)")
    phone = fields.Char(string='Phone', required=True)
    email = fields.Char(string='Email')
    mobile = fields.Char(string="Mobile")
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street 2")

    country_id = fields.Many2one(
        comodel_name='res.country', string="Country",
        default=lambda self: self.env.company.country_id,
    )
    state_id = fields.Many2one(
        comodel_name='res.country.state', string="State",
        default=lambda self: self.env.company.state_id,
    )
    city = fields.Char(string="City")
    zip = fields.Char(string="ZIP Code")
    notes = fields.Text(string="Notes")
    partner_id = fields.Many2one(
        comodel_name='res.partner', string="Contact",
    )

    # Owner
    # owner = fields.Many2one(
    #     'pod_clinic.practice', string='Owner', store=True, readonly=False)
    # owner_id = fields.Integer(
    #     related='owner.id', string='Doctor Owner ID')
    # owner_name = fields.Char(
    #     related='owner.name', string='Owner Name')
    # Practices
    practice = fields.One2many(
        'pod_clinic.practice', 'owner', string='Practice')
    practice_count = fields.Integer(compute='compute_practice_count')

    # Patients
    patient = fields.One2many('pod_clinic.patient', 'owner', string='Patient')
    patient_count = fields.Integer(compute='compute_patient_count')
    # Prescription
    prescription = fields.One2many(
        'pod_clinic.prescription', 'owner', string='Prescription')
    prescription_count = fields.Integer(compute='compute_prescription_count')

    # Item
    item_service = fields.Many2many(
        'pod_clinic.item', string='Accommodation', domain="[('item_type', '=', 'service')]")

    @api.model
    def create(self, vals):
        if vals.get('doctor_id', _('New')) == _('New'):
            vals['doctor_id'] = self.env['ir.sequence'].next_by_code(
                'doctor.seq') or _('New')
        result = super(Doctor, self).create(vals)
        return result

     # Button Patient Handle

    def open_doctor_patient(self):
        return {
            'name': _('Patients'),
            'domain': [('doctor', '=', self.id)],
            'view_type': 'form',
            'res_model': 'pod_clinic.patient',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }
    # Button Patient Count

    def compute_patient_count(self):
        for record in self:
            record.patient_count = self.env['pod_clinic.patient'].search_count(
                [('doctor', '=', self.id)])

    # Button Prescription Handle
    def open_doctor_prescription(self):
        return {
            'name': _('Prescriptions'),
            'domain': [('doctor', '=', self.id)],
            'view_type': 'form',
            'res_model': 'pod_clinic.prescription',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    # Button Prescription Count
    def compute_prescription_count(self):
        for record in self:
            record.prescription_count = self.env['pod_clinic.prescription'].search_count(
                [('doctor', '=', self.id)])
