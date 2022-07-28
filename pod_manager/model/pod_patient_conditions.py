# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime


class pod_patient_conditions(models.Model):
    _name = 'pod.patient.conditions'
    _description = 'podiatry patient conditions'

    pathelogh_id = fields.Many2one('pod.pathology', 'Pathology')
    # status_of_the_condition = fields.Selection([('chronic', 'Chronic'), ('status quo', 'Status Quo'), (
    #     'healed', 'Healed'), ('improving', 'Improving'), ('worsening', 'Worsening')], 'Status of the condition')
    is_active = fields.Boolean('Active Pathology')
    # diagnosed_date = fields.Date('Date of Diagnosis')
    # age = fields.Date('Age when diagnosed')
    # condition_severity = fields.Selection(
    #     [('mild', 'Mild'), ('moderate', 'Moderate'), ('severe', 'Severe')], 'Severity')
    # is_infectious = fields.Boolean(
    #     'Infectious Pathology', help='Check if the patient has an infectious / transmissible condition')
    short_comment = fields.Char('Remarks')
    # healed_date = fields.Date('Healed')
    doctor_id = fields.Many2one('pod.patient', 'Doctor')
    # is_allergy = fields.Boolean('Allergic Pathology')
    # is_infectious = fields.Boolean('Infectious Pathology')
    # allergy_type = fields.Selection([('drug_allergy', 'Drug Allergy'), (
    #     'food_allergy', 'Food Allergy'), ('misc', 'Misc')], 'Allergy_type')
    # pregnancy_warning = fields.Boolean('Pregnancy warning')
    # weeks_of_pregnancy = fields.Integer('Contracted in pregnancy week #')
    # is_on_treatment = fields.Boolean('Currently on Treatment')
    # treatment_description = fields.Char('Treatment Description')
    # date_start_treatment = fields.Date('Start of treatment')
    # date_stop_treatment = fields.Date('End of treatment')
    psc_code_id = fields.Many2one('psc.code', 'Code')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
