# -*- coding: utf8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EPrescriptionWizard(models.TransientModel):
    _name = "podiatry.prescription.wizard"
    _description = "Prescription Wizard"
    _rec_name = 'reference_no'

    doctor_id = fields.Many2one(
        'podiatry.doctor', string="Doctor", required=True)
    practice_id = fields.Many2one(string="Practice ID",
                                  related="doctor_id.practice_id")

    patient_id = fields.Many2one(
        'podiatry.patient', string="Patient", required=True)
    patient_name = fields.Char(string="Hasta Ad", related="patient_id.name")
    patient_surname = fields.Char(
        string="Hasta Soyad", related="patient_id.surname")

    recete_tur = fields.Selection([
        ('1', 'Normal'),
        ('2', 'Red'),
        ('3', 'Orange'),
        ('4', 'Purple'),
        ('5', 'Green')
    ], string="Prescription Type", required=True)
    recete_alt_tur = fields.Selection([
        ('1', 'Custom'),
        ('2', 'OTC'),
        ('3', 'Brace'),
        ('4', 'Repair'),
    ], string="Device Type", required=True)

    rush_order = fields.Boolean('Rush Order')
    make_quantity = fields.Boolean('Qty to make')
    make_from_prior_rx = fields.Boolean('Make from prior rx')
    ship_to_patient = fields.Boolean('Ship to patient')
    make_left_only = fields.Boolean('Make left device only')
    make_right_only = fields.Boolean('Make right device only')
    make_bilateral = fields.Boolean('Make left / right pair')

    facility_code = fields.Char(string="Facility Code")
    tracking_no = fields.Char(string="Tracking No")
    provizyon_tip = fields.Selection([
        ('1', 'Normal'),
        ('2', 'Trafik'),
        ('3', 'Doğal Afet'),
        ('4', 'Adli Vaka'),
        ('5', 'İş Kazası'),
        ('6', 'Meslek Hastalığı'),
        ('7', 'Analık Hali'),
        ('8', '3713/21')
    ], string="Provision Type", required=True)
    protokol_no = fields.Char(string="Protocol No")
    reference_no = fields.Char(string="Rx ID")

    address_no = fields.Char(string="Prescriptions No")
    erecete_aciklama_turu = fields.Integer(
        string="Prescriptions Açıklama Type")
    erecete_aciklama = fields.Char(string="Prescriptions Açıklama")
    erecete_tani_kodu = fields.Char(string="Prescriptions Tanı Kodu")
    erecete_tani_adi = fields.Char(string="Prescriptions Tanı Adı")

    today = fields.Date(
        string='Date', default=fields.Date.context_today, date_format="dd.MM.yyyy")

    pharmacy_line_ids = fields.One2many(
        'prescription.pharmacy.lines2', 'prescription_id', string="Pharmacy Lines", required=True)
    explanation_line_ids = fields.One2many('prescription.explanation.lines', 'prescription_id',
                                           string="Explanation Lines", required=True)

    diagnosis_line_ids = fields.Many2many(
        'podiatry.diagnosis', string="Diagnosises", required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Medulaya Sent'),
        ('deleted', 'Prescriptions Deleted')
    ], default="draft", string="Durum")
