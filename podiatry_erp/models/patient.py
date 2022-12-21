# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class Patient(models.Model):
    _name = "podiatry.patient"
    _inherits = {
        'res.partner': 'partner_id',
    }

    _rec_name = 'patient_id'
    create_users_button = fields.Boolean()
    # user_id = fields.Many2one('res.users')
    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='restrict',
                                 help='Partner-related data of the Doctor')
    patient_id = fields.Many2many('res.partner', domain=[(
        'is_patient', '=', True)], string="Patient", required=True)
    practice_id = fields.Many2one(
        comodel_name='podiatry.practice',
        string="Practice",
    )
    doctor_id = fields.Many2one(
        comodel_name='podiatry.doctor',
        string='Practitioner')

    image1 = fields.Binary("Right photo")
    image2 = fields.Binary("Left photo")

    left_obj_model = fields.Binary("Left Obj")
    left_obj_file_name = fields.Char(string="Left Obj File Name")
    right_obj_model = fields.Binary("Right Obj")
    right_obj_file_name = fields.Char(string="Right Obj File Name")

    doctor_reference = fields.Char(related='doctor_id.name', readonly=True)

    is_patient = fields.Boolean()

    gender = fields.Selection(selection=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string="Gender")

    dob = fields.Date()
    patient_age = fields.Integer(compute='_cal_age', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='restrict',
                                 help='Partner-related data of the Patient')

    active = fields.Boolean(string="Active", default=True, tracking=True)
    color = fields.Integer(string="Color Index (0-15)")

    prescription_count = fields.Integer(
        string='Prescription Count', compute='_compute_prescription_count')

    prescription_id = fields.One2many(
        comodel_name='medical.prescription',
        inverse_name='patient_id',
        string="Prescriptions",
    )

    notes = fields.Text(string="Notes")

    def _compute_prescription_count(self):
        for rec in self:
            prescription_count = self.env['medical.prescription'].search_count(
                [('patient_id', '=', rec.id)])
            rec.prescription_count = prescription_count

    prescription_date = fields.Datetime(
        'Prescription Date', default=fields.Datetime.now)

    @api.onchange('patient_id')
    def _onchange_patient(self):
        '''
        The purpose of the method is to define a domain for the available
        purchase orders.
        '''
        address_id = self.patient_id
        self.patient_address_id = address_id

    patient_address_id = fields.Many2one('res.partner', string="Address", )

    same_reference_patient_id = fields.Many2one(
        comodel_name='podiatry.patient',
        string='Patient with same Identity',
        compute='_compute_same_reference_patient_id',
    )

    @api.depends('ref')
    def _compute_same_reference_patient_id(self):
        for patient in self:
            domain = [
                ('ref', '=', patient.ref),
            ]

            origin_id = patient._origin.id

            if origin_id:
                domain += [('id', '!=', origin_id)]

            patient.same_reference_patient_id = bool(patient.reference) and \
                self.with_context(active_test=False).sudo().search(
                    domain, limit=1)

    @api.model
    def _default_image(self):
        image_path = get_module_resource(
            'podiatry_erp', 'static/src/description', 'avatar_gray.png')
        return base64.b64encode(open(image_path, 'rb').read())

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)

    @api.depends('dob')
    def _cal_age(self):
        for record in self:
            if record.dob:
                years = relativedelta(date.today(), record.dob).years
                record.patient_age = str(int(years))
            else:
                record.patient_age = 0

    def create_patient(self):
        self.is_patient = True
        if len(self.partner_id.user_ids):
            raise UserError(_('User for this patient already created.'))
        else:
            self.create_users_button = False
        patient_id = []

        patient_id.append(self.env['res.groups'].search(
            [('name', '=', 'Patient')]).id)
        patient_id.append(self.env['res.groups'].search(
            [('name', '=', 'Internal User')]).id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Name ',
            'view_mode': 'form',
            'view_id': self.env.ref("patient.view_create_user_wizard_form").id,
            'target': 'new',
            'res_model': 'res.users',
            'context': {'default_partner_id': self.partner_id.id, 'default_is_patient': True,
                        'default_groups_id': [(6, 0, patient_id)]}

        }

    def name_get(self):
        result = []
        for rec in self:
            name = '[' + rec.ref + '] ' + rec.name
            result.append((rec.id, name))
        return result

    def write(self, values):
        result = super(Patient, self).write(values)
        if 'user_id' in values or 'other_partner_ids' in values:
            self._add_followers()
        return result

    def copy(self, default=None):
        for rec in self:
            raise UserError(_('You Can Not Duplicate patient.'))

    def action_open_prescriptions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'medical.prescription',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }
