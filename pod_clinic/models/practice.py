# -*- coding: utf-8 -*-

import base64
from odoo import models, fields, api, _
from odoo.modules.module import get_module_resource


class Practice(models.Model):
    _name = 'pod_clinic.practice'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _rec_name = 'name'
    practice_id = fields.Char(string='ID', required=True, copy=False, readonly=True,
                              index=True, default=lambda self: _('New'))
    name = fields.Char(string="Name", required=True)
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

    # Doctors
    doctor = fields.One2many('pod_clinic.doctor', 'owner', string='Doctor')
    doctor_count = fields.Integer(compute='compute_doctor_count')
    # Patients
    patient = fields.One2many('pod_clinic.patient', 'owner', string='Patient')
    patient_count = fields.Integer(compute='compute_patient_count')
    # Prescriptions
    prescription = fields.One2many(
        'pod_clinic.prescription', 'owner', string='Prescription')
    prescription_count = fields.Integer(compute='compute_prescription_count')

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'pc', 'static/avatar', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    @api.model
    def create(self, vals):
        if vals.get('practice_id', _('New')) == _('New'):
            vals['practice_id'] = self.env['ir.sequence'].next_by_code(
                'practice.seq') or _('New')
        result = super(Practice, self).create(vals)
        return result

    # Button Doctor Handle
    def open_practice_doctor(self):
        return {
            'name': _('Doctors'),
            'domain': [('owner', '=', self.id)],
            'view_type': 'form',
            'res_model': 'pod_clinic.doctor',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
        }

    # Button Doctor Count
    def compute_doctor_count(self):
        for record in self:
            record.doctor_count = self.env['pod_clinic.doctor'].search_count(
                [('owner', '=', self.id)])

    # Button Patient Handle

    def open_practice_patient(self):
        return {
            'name': _('Patients'),
            'domain': [('owner', '=', self.id)],
            'view_type': 'form',
            'res_model': 'pod_clinic.patient',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
        }
    # Button Patient Count

    def compute_patient_count(self):
        for record in self:
            record.patient_count = self.env['pod_clinic.patient'].search_count(
                [('owner', '=', self.id)])

    # Button Prescription Handle
    def open_practice_prescription(self):
        return {
            'name': _('Prescriptions'),
            'domain': [('owner_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'pod_clinic.prescription',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
        }

    # Button Prescription Count
    def compute_prescription_count(self):
        for record in self:
            record.prescription_count = self.env['pod_clinic.prescription'].search_count(
                [('owner_id', '=', self.id)])
