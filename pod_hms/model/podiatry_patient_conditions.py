# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime


class podiatry_patient_conditions(models.Model):
    _name = 'podiatry.patient.conditions'
    _description = 'podiatry patient conditions'

    pathelogh_id = fields.Many2one('podiatry.pathology', 'Condition')
    status_of_the_condition = fields.Selection([('chronic', 'Chronic'), ('status quo', 'Status Quo'), (
        'healed', 'Healed'), ('improving', 'Improving'), ('worsening', 'Worsening')], 'Status of the condition')
    is_active = fields.Boolean('Active Condition')
    diagnosed_date = fields.Date('Date of Diagnosis')
    age = fields.Date('Age when diagnosed')
    condition_severity = fields.Selection(
        [('mild', 'Mild'), ('moderate', 'Moderate'), ('severe', 'Severe')], 'Severity')
    is_infectious = fields.Boolean(
        'Infectious Condition', help='Check if the patient has an infectious / transmissible condition')
    short_comment = fields.Char('Remarks')
    healed_date = fields.Date('Healed')
    practitioner_id = fields.Many2one('podiatry.patient', 'Practitioner')
    is_allergy = fields.Boolean('Allergic Condition')
    is_infectious = fields.Boolean('Infectious Condition')
    allergy_type = fields.Selection([('product_allergy', 'Product Allergy'), (
        'food_allergy', 'Food Allergy'), ('misc', 'Misc')], 'Allergy_type')

    is_on_treatment = fields.Boolean('Currently on Treatment')
    treatment_description = fields.Char('Treatment Description')
    date_start_treatment = fields.Date('Start of treatment')
    date_stop_treatment = fields.Date('End of treatment')
    podiatry_products_services_code_id = fields.Many2one(
        'podiatry.products.services.code', 'Code')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
