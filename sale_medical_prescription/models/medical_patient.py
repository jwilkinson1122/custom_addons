# Copyright 2017 LasLabs Inc.
# Copyright 2020 LabViv.
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html)

from odoo import fields, models


class MedicalPatient(models.Model):
    _inherit = 'medical.patient'

    safety_cap_yn = fields.Boolean(
        string='Use Safety Cap',
        help='Does the patient prefer a safety cap on their prescription?',
    )
    counseling_yn = fields.Boolean(
        string='Provide Counseling',
        help='Does the patient require counseling on their prescription?'
    )
    allergies = fields.Char()
    existing_meds = fields.Char()
