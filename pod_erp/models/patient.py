# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class Patient(models.Model):
    _name = "podiatry.patient"
    _inherits = {
        'res.partner': 'partner_id',
    }
    create_users_button = fields.Boolean()
    # user_id = fields.Many2one('res.users')
    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='restrict',
                                 help='Partner-related data of the Patient')

    practice_id = fields.Many2one(
        comodel_name='podiatry.practice',
        required=True,
        string="Practice",
    )
    practitioner_id = fields.Many2one(
        comodel_name='podiatry.practitioner',
        required=True,
        string='Practitioner')

    is_patient = fields.Boolean()
    dob = fields.Date()
    patient_age = fields.Integer(compute='_cal_age', readonly=True)
    prescription_count = fields.Integer(compute='get_prescription_count')

    def open_patient_prescriptions(self):
        for records in self:
            return {
                'name': _('Prescription'),
                'view_type': 'form',
                'domain': [('patient', '=', records.id)],
                'res_model': 'podiatry.prescription',
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_patient': self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['podiatry.prescription'].search_count(
                [('patient', '=', records.id)])
            records.prescription_count = count

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
