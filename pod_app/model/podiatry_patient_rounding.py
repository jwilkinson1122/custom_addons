# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class podiatry_patient_rounding(models.Model):
    _name = "podiatry.patient.rounding"
    _description = 'Podiatry patient rounding'
    _rec_name = 'podiatry_inpatient_registration'

    @api.onchange('right_pupil', 'left_pupil')
    def onchange_duration(self):
        if self.left_pupil == self.right_pupil:
            self.anisocoria = False
        else:
            self.anisocoria = True

    podiatry_inpatient_registration = fields.Many2one(
        'podiatry.inpatient.registration', string="Registration Code", required=True)
    health_physician_id = fields.Many2one(
        'podiatry.physician', string="Health Professional", readonly=True)
    evaluation_start = fields.Datetime(string="Start", required=True)
    evaluation_end = fields.Datetime(string="End", required=True)
    environmental_assessment = fields.Char(string='Environment')
    icu_patient = fields.Boolean(string='ICU')
    warning = fields.Boolean(string='Warning')
    pain = fields.Boolean(string='Pain')
    potty = fields.Boolean(string='Potty')
    position = fields.Boolean(string='Position')
    proximity = fields.Boolean(string='Proximity')
    pump = fields.Boolean(string='Pumps')
    personal_needs = fields.Boolean(string='Personal Needs')
    temperature = fields.Float(string='Temperature')
    systolic = fields.Integer(string="Systolic Pressure")
    diastolic = fields.Integer(string='Diastolic Pressure')
    bpm = fields.Integer(string='Heart Rate')
    respiratory_rate = fields.Integer(string="Respiratory Rate")
    osat = fields.Integer(string="Oxygen Saturation")
    diuresis = fields.Integer(string="Diuresis")
    urinary_catheter = fields.Boolean(string="Urinary Catheter")
    glycemia = fields.Integer(string="Glycemia")
    depression = fields.Boolean(string="Depression Signs")
    evolution = fields.Selection([('n', 'Status Quo'),
                                  ('i', 'Improving'),
                                  ('w', 'Worsening')],
                                 string="Evolution")
    round_summary = fields.Text(string="Round Summary")
    gcs = fields.Many2one("podiatry.icu.glasgow", string="GCS")
    right_pupil = fields.Integer(string="R")
    pupillary_reactivity = fields.Selection([('brisk', 'Brisk'),
                                             ('sluggish', 'Sluggish'),
                                             ('nonreactive', 'Nonreactive')],
                                            string="Pupillary_Reactivity")
    pupil_dilation = fields.Selection([('normal', 'Normanl'),
                                       ('miosis', 'Miosis'),
                                       ('mydriasis', 'Mydriasis')],
                                      string="Pupil Dilation")
    left_pupil = fields.Integer(string="l")
    anisocoria = fields.Boolean(string="Anisocoria")
    pupil_consensual_resp = fields.Boolean(string=" Consensual Response ")
    oxygen_mask = fields.Boolean(string='Oxygen Mask')
    respiration_type = fields.Selection([('regular', 'Regular'),
                                         ('deep', 'Deep'),
                                         ('shallow', 'Shallow'),
                                         ('labored', 'Labored'),
                                         ('intercostal', 'Intercostal')],
                                        string="Respiration")
    peep = fields.Boolean(string='Peep')
    sce = fields.Boolean(string='SCE')
    lips_lesion = fields.Boolean(string="Lips Lesion")
    fio2 = fields.Integer(string="FiO2")
    trachea_alignment = fields.Selection([('midline', 'Midline'),
                                          ('right', 'Deviated Right'),
                                          ('left', 'Deviated Left')],
                                         string=' Tracheal alignment ')
    oral_mucosa_lesion = fields.Boolean(string=' Oral mucosa lesion ')
    chest_expansion = fields.Selection([('symmentric', 'Symmentrical'),
                                        ('asymmentric', 'Asynmmentrical')],
                                       string="Expansion")
    paradoxical_expansion = fields.Boolean(string="Paradoxical")
    tracheal_tug = fields.Boolean(string='Tracheal Tug')
    xray = fields.Binary(string="Xray")
    chest_drainages = fields.One2many(
        'podiatry.icu.chest_drainage', 'podiatry_patient_rounding_chest_drainage_id', string="Chest Drainages")
    ecg = fields.Many2one('podiatry.icu.ecg', string="ECG")
    venous_access = fields.Selection([('none', 'None'),
                                      ('central', 'Central Catheter'),
                                      ('peripheral', 'Peripheral')],
                                     string="Venous Access")
    swan_ganz = fields.Boolean(string='Swan Ganz')
    arterial_access = fields.Boolean(string='Arterial Access')
    dialysis = fields.Boolean(string="Dialysis")
    edema = fields.Selection([('none', 'None'),
                              ('peripheral', 'Peripheral'),
                              ('anasarca', 'Anasarca')],
                             string='Edema')
    bacteremia = fields.Boolean(string="Becteremia")
    ssi = fields.Boolean(string='Surgery Site Infection')
    wound_dehiscence = fields.Boolean(string='Wound Dehiscence')
    cellulitis = fields.Boolean(string="Cellulitis")
    necrotizing_fasciitis = fields.Boolean(string=' Necrotizing fasciitis ')
    vomiting = fields.Selection([('none', 'None'),
                                 ('vomiting', 'Vomiting'),
                                 ('hematemesis', 'Hematemesis ')],
                                string="Vomiting")
    bowel_sounds = fields.Selection([('normal', 'Normal'),
                                     ('increased', 'Increased'),
                                     ('decreased', 'Decreased'),
                                     ('absent', 'Absent')],
                                    string="Bowel Sounds")
    stools = fields.Selection([('normal', 'Normal'),
                               ('constipation', 'Constipation'),
                               ('diarrhea', 'Diarrhea'),
                               ('melena', 'Melena')],
                              string="Stools")
    peritonitis = fields.Boolean(string="Peritonitis")
    procedures_ids = fields.One2many(
        'podiatry.rounding_procedure', 'podiatry_patient_rounding_procedure_id', string="Procedures")
    practice_location_id = fields.Many2one(
        'stock.location', string='Care Location')
    treatments_ids = fields.One2many(
        'podiatry.patient.rounding.treatment', 'podiatry_patient_rounding_treatment_id', string="Treatments")
    podiatry_supplies_ids = fields.One2many(
        'podiatry.patient.rounding.podiatry_supply', 'podiatry_patient_rounding_podiatry_supply_id', string='Podiatry Supplier')
    vaccines_ids = fields.One2many(
        'podiatry.patient.rounding.vaccine', 'podiatry_patient_rounding_vaccine_id', string='Vaccines')
    state = fields.Selection([('draft', 'Draft'),
                              ('done', 'Done')],
                             string="Status")
