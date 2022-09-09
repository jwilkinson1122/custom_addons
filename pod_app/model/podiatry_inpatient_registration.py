# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from datetime import date, datetime


class podiatry_inpatient_registration(models.Model):
    _name = 'podiatry.inpatient.registration'
    _description = 'Podiatry Inpatient Registration'

    name = fields.Char(string="Registration Code",
                       copy=False, readonly=True, index=True)
    patient_id = fields.Many2one(
        'podiatry.patient', string="Patient", required=True)
    care_date = fields.Datetime(
        string="Care date", required=True)
    discharge_date = fields.Datetime(
        string="Expected Discharge date", required=True)
    attending_physician_id = fields.Many2one(
        'podiatry.physician', string="Attending Physician")
    operating_physician_id = fields.Many2one(
        'podiatry.physician', string="Operating Physician")
    admission_type = fields.Selection([('routine', 'Routine'), ('maternity', 'Maternity'), ('elective', 'Elective'), (
        'urgent', 'Urgent'), ('emergency', 'Emergency  ')], required=True, string="Admission Type")
    podiatry_pathology_id = fields.Many2one(
        'podiatry.pathology', string="Reason for Admission")
    info = fields.Text(string="Extra Info")
    bed_transfers_ids = fields.One2many(
        'bed.transfer', 'inpatient_id', string='Transfer Bed', readonly=True)
    podiatry_diet_belief_id = fields.Many2one(
        'podiatry.diet.belief', string='Belief')
    therapeutic_diets_ids = fields.One2many(
        'podiatry.inpatient.diet', 'podiatry_inpatient_registration_id', string='Therapeutic_diets')
    diet_vegetarian = fields.Selection([('none', 'None'), ('vegetarian', 'Vegetarian'), ('lacto', 'Lacto Vegetarian'), (
        'lactoovo', 'Lacto-Ovo-Vegetarian'), ('pescetarian', 'Pescetarian'), ('vegan', 'Vegan')], string="Vegetarian")
    nutrition_notes = fields.Text(string="Nutrition notes / Directions")
    state = fields.Selection([('free', 'Free'), ('confirmed', 'Confirmed'), ('practiceized',
                             'Practiceized'), ('cancel', 'Cancel'), ('done', 'Done')], string="State", default="free")
    nursing_plan = fields.Text(string="Nursing Plan")
    discharge_plan = fields.Text(string="Discharge Plan")
    icu = fields.Boolean(string="ICU")
    device_ids = fields.One2many(
        'podiatry.inpatient.device', 'podiatry_inpatient_registration_id', string='Device')

    @api.model
    def default_get(self, fields):
        result = super(podiatry_inpatient_registration,
                       self).default_get(fields)
        patient_id = self.env['ir.sequence'].next_by_code(
            'podiatry.inpatient.registration')
        if patient_id:
            result.update({
                'name': patient_id,
            })
        return result

    def registration_confirm(self):
        self.write({'state': 'confirmed'})

    def registration_admission(self):
        self.write({'state': 'practiceized'})

    def registration_cancel(self):
        self.write({'state': 'cancel'})

    def patient_discharge(self):
        self.write({'state': 'done'})


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
