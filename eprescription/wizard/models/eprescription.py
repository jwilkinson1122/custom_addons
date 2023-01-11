# -*- coding: utf8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EPrescriptionWizard(models.TransientModel):
    _name = "hospital.eprescription.wizard"
    _description = "E-Prescription Wizard"
    _rec_name = 'seri_no'

    doctor_id = fields.Many2one(
        'hospital.doctor', string="Doctor", required=True)
    brans_kod = fields.Char(string="Branch Code",
                            related="doctor_id.brans_kod")

    patient_id = fields.Many2one(
        'hospital.epatient', string="Patient", required=True)
    patient_name = fields.Char(string="Hasta Ad", related="patient_id.name")
    patient_surname = fields.Char(
        string="Hasta Soyad", related="patient_id.surname")

    recete_tur = fields.Selection([
        ('1', 'Normal'),
        ('2', 'Red'),
        ('3', 'Orange'),
        ('4', 'Purple'),
        ('5', 'Green')
    ], string="Prescriptions Type", required=True)
    recete_alt_tur = fields.Selection([
        ('1', 'Walk In Prescription'),
        ('2', 'Inpatient Prescription'),
        ('3', 'Discharge Prescription'),
        ('4', 'Daily Prescription'),
        ('5', 'Rush Prescription'),
        ('6', 'Green Alan Prescription'),
        ('7', 'Home Prescription'),
        ('8', 'Mobile Prescription')
    ], string="Prescriptions Alt Type", required=True)

    tesis_kod = fields.Char(string="Facility Code")
    takip_no = fields.Char(string="Takip No")
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
    seri_no = fields.Char(string="Seri No")

    erecete_no = fields.Char(string="E-Prescriptions No")
    erecete_aciklama_turu = fields.Integer(
        string="E-Prescriptions Açıklama Type")
    erecete_aciklama = fields.Char(string="E-Prescriptions Açıklama")
    erecete_tani_kodu = fields.Char(string="E-Prescriptions Tanı Kodu")
    erecete_tani_adi = fields.Char(string="E-Prescriptions Tanı Adı")

    today = fields.Date(
        string='Date', default=fields.Date.context_today, date_format="dd.MM.yyyy")

    pharmacy_line_ids = fields.One2many(
        'eprescription.pharmacy.lines2', 'eprescription_id', string="Pharmacy Lines", required=True)
    explanation_line_ids = fields.One2many('eprescription.explanation.lines', 'eprescription_id',
                                           string="Explanation Lines", required=True)

    diagnosis_line_ids = fields.Many2many(
        'hospital.diagnosis', string="Diagnosises", required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Medulaya Sent'),
        ('deleted', 'E-Prescriptions Deleted')
    ], default="draft", string="Durum")
