# -*- coding: utf-8 -*-

import logging
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class InheritedResPartner(models.Model):
    _inherit = 'res.partner'

    is_patient = fields.Boolean(string='Patient')
    is_person = fields.Boolean(string="Person")
    is_doctor = fields.Boolean(string="Doctor")
    # is_insurance_company = fields.Boolean(string='Insurance Company')
    # patient_insurance_ids = fields.One2many('pod.insurance', 'patient_id')
    is_practice = fields.Boolean('Practice')

    is_active = fields.Boolean('Is Active')

    reference = fields.Char('ID Number')

    clinic_role_ids = fields.Many2many(
        string="Clinic User Roles", comodel_name="clinic.role"
    )

    dob = fields.Date()
    age = fields.Integer(compute='_cal_age', store=True, readonly=True)

    prescription_count = fields.Integer(compute='get_prescription_count')

    def open_customer_prescriptions(self):
        for records in self:
            return {
                'name': _('Prescription History'),
                'view_type': 'form',
                'domain': [('customer', '=', records.id)],
                'res_model': 'dr.prescription',
                'view_id': False,
                'view_mode': 'tree,form',
                'context': {'default_customer': self.id},
                'type': 'ir.actions.act_window',
            }

    def get_prescription_count(self):
        for records in self:
            count = self.env['dr.prescription'].search_count(
                [('customer', '=', records.id)])
            records.prescription_count = count

    @api.depends('dob')
    def _cal_age(self):
        for record in self:
            if record.dob:
                years = relativedelta(date.today(), record.dob).years
                record.age = str(int(years))
            else:
                record.age = 0
