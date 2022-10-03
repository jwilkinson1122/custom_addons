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
    # partner_id = fields.Many2one(
    #     comodel_name='res.partner', string="Contact",
    # )

    # Doctor -> Type
    # doctor_type = fields.Many2one('pod_clinic.doctor.type',
    #                               string='Specialty')
    # doctor_type_name = fields.Char(related='doctor_type.name',
    #                                string='Specialty')

    # Doctor -> Role
    # doctor_role = fields.Many2one('pod_clinic.doctor.role', domain="[('doctor_type','=',doctor_type)]",
    #                               string='Role')
    # doctor_role_name = fields.Char(related='doctor_role.name',
    #                                string='Role')

    # Owner
    owner = fields.Many2one(
        'pod_clinic.doctor', string='Owner', store=True, readonly=False)
    owner_id = fields.Integer(
        related='owner.id', string='Doctor Owner ID')
    owner_name = fields.Char(
        related='owner.name', string='Owner Name')

    # Prescription count
    # prescription_count = fields.Integer(compute='compute_prescription_count')
    # Patient count
    # patient_count = fields.Integer(compute='compute_patient_count')

    # Patients
    patient = fields.One2many('pod_clinic.patient', 'owner', string='Patient')
    patient_count = fields.Integer(compute='compute_patient_count')

    # Prescription
    prescription = fields.One2many(
        'pod_clinic.prescription', 'owner', string='Prescription')
    prescription_count = fields.Integer(compute='compute_prescription_count')

    # @api.depends('name', 'doctor_type_name', 'doctor_role_name')
    # def _compute_fields_rec_name(self):
    #     for doctor in self:
    #         if(doctor.doctor_type_name == False and doctor.doctor_role_name == False):
    #             doctor.rec_name = '{}'.format(doctor.name)
    #         elif(doctor.doctor_role_name == False):
    #             doctor.rec_name = '{} - {}'.format(doctor.name,
    #                                                doctor.doctor_type_name)
    #         elif(doctor.doctor_type_name == False):
    #             doctor.rec_name = '{}'.format(doctor.name)
    #         else:
    #             doctor.rec_name = '{} - {} {}'.format(doctor.name,
    #                                                   doctor.doctor_type_name, doctor.doctor_role_name)

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

    # Button Prescription Handle
    def open_doctor_prescription(self):
        return {
            'name': _('Prescriptions'),
            'domain': [('doctor', '=', self.id)],
            'view_type': 'form',
            'res_model': 'pod_clinic.prescription',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
        }

    # Button Prescription Handle
    def open_doctor_patient(self):
        return {
            'name': _('Patients'),
            'domain': [('doctor', '=', self.id)],
            'view_type': 'form',
            'res_model': 'pod_clinic.patient',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
        }

    # Button Prescription Count
    def compute_prescription_count(self):
        for record in self:
            record.prescription_count = self.env['pod_clinic.prescription'].search_count(
                [('doctor', '=', self.id)])

        # Button Patient Count
    def compute_patient_count(self):
        for record in self:
            record.patient_count = self.env['pod_clinic.patient'].search_count(
                [('doctor', '=', self.id)])


# class DoctorType(models.Model):
#     _name = 'pod_clinic.doctor.type'
#     name = fields.Char(string='Name', required=True)


# class DoctorRole(models.Model):
#     _name = 'pod_clinic.doctor.role'
#     name = fields.Char(string='Name', required=True)
#     doctor_type = fields.Many2one('pod_clinic.doctor.type',
#                                   string='Type', required=True)
