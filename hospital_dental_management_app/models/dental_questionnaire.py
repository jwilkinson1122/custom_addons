# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DentalQuestionnaire(models.Model):
    _name = 'dental.questionnaire'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'patient_id'
    _description = 'Dental Questionnaire'

    # Identification Details

    # name = fields.Char(string="Name")
    patient_id = fields.Many2one('res.partner', string='Patient')
    date = fields.Datetime(string='Date', default=fields.Datetime.now())
    partner_id = fields.Many2one('res.partner', string='Referring')
    treatment = fields.Boolean(string='Have you ever taken an anti-biotic prior to dental treatment?')
    previously = fields.Boolean(string='Have you previously had any Dental treatments?')
    previously_note = fields.Text(string="If Yes Describe")
    anesthetic = fields.Boolean(string='Have you ever had any problem associated with dental anesthetic?')
    rate = fields.Selection([('no','No Problem'),('slight','Slight'),('Moderate','moderate'),('wild','Wild Horses Have To Drag Me In')],default='no')
    allergies = fields.Boolean(string='Do you suffer from any allergies?')
    allergies_note = fields.Text(string="If Yes Describe")
    reaction = fields.Boolean(string='Have you ever had a peculiar or adverse reaction to any medications or injections')
    reaction_note = fields.Text(string="If Yes Describe")

    asthma = fields.Boolean(string='Do you have or ever had asthma?')
    heart = fields.Boolean(string='Do you have or ever had any heart or blood pressure problems?')
    artificial = fields.Boolean(string='Do you have a prosthetic or artificial joint?')

    bleeding = fields.Boolean(string='Do you have a bleeding problem or bleeding disorder')
    infections = fields.Boolean(string='Do you have any teeth infections?')
    infections_note = fields.Text(string="If Yes Describe")



    disease_type_ids = fields.Many2many('disease.type', 'rel_disease_dental_question', 'queation_id', 'disease_type_id',
                                        string='History of Any Teeth Problem')
    procedures_ids = fields.Many2many('patient.procedures.type', 'rel_procedures_dental_question', 'queation_id',
                                      'procedures_id', string='What Dental Procedures are you intersted in?')
    note = fields.Text(string="Please describe any problems you have had with past dental experiences")
    immediate = fields.Text(string="What is your immediate dental concern?")
    care = fields.Text(string="How do you care for your mouth?")
    appearance = fields.Text(string="These are some things that are important about my dental health and appearance:?")


