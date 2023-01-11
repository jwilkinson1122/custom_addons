# -*- coding: utf8 -*-

from odoo import models, fields, api


class EPrescriptions(models.TransientModel):
    _name = "hospital.eprescription.query.wizard"
    _description = "E-Prescription wizard"

    doctor_id = fields.Many2one(
        'hospital.doctor', string="Doctor", required=True)
    brans_kod = fields.Char(string="Branch Code",
                            related="doctor_id.brans_kod")

    patient_id = fields.Many2one(
        'hospital.epatient', string="Patient", required=True)
    patient_name = fields.Char(string="Hasta Ad", related="patient_id.name")
    patient_surname = fields.Char(
        string="Hasta Soyad", related="patient_id.surname")

    recete_tur = fields.Integer(string="Prescriptions Type", required=True)
    recete_alt_tur = fields.Integer(
        string="Prescriptions Alt Type", required=True)

    tesis_kod = fields.Char(string="Facility Code")
    takip_no = fields.Char(string="Takip No")
    provizyon_tip = fields.Integer(string="Provision Type")
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


# İlaç ekle
class AppointmentPharmacyLines(models.TransientModel):
    _name = "eprescription.pharmacy.lines.wizard"
    _description = "E-Prescription Pharmacy Lines"

    kullanim_sekli = fields.Integer(string="Kullanım Şekli")
    kullanim_doz1 = fields.Integer(string="Kullanım Doz 1")
    kullanim_doz2 = fields.Float(string="Kullanım Doz 2")
    kullanim_periyot = fields.Integer(string="Kullanım Periyodu")
    kullanim_periyot_birimi = fields.Selection([
        ('3', 'Günde'),
        ('4', 'Haftada'),
        ('5', 'Ayda'),
        ('6', 'Yılda')
    ], string="Kullanım Periyot Birimi")
    quantity = fields.Integer(string="Adet", default=1)

    erecete_ilac_aciklama_turu = fields.Selection([
        ('1', 'Teşhis/Tanı'),
        ('2', 'Tedavi Süresi'),
        ('3', 'Hasta Güvenlik ve İzleme Formu'),
        ('4', 'Tetkik Sonucu'),
        ('5', 'Endikasyon Dışı Kullanım İzni'),
        ('99', 'Other')
    ], string="E-Prescriptions İlaç Açıklama Type")
    erecete_ilac_aciklama = fields.Text(string="E-Prescriptions İlaç Açıklama")

    eprescription_id = fields.Many2one('hospital.eprescription')
    # sub_total = fields.Float(string="Total", compute="_compute_sub_total")


# E-Prescriptions Add Description
class EprescriptionsExplanationLines(models.TransientModel):
    _name = "eprescription.explanation.lines.wizard"
    _description = "E-Prescription Explanation Lines"

    explanation_id = fields.Many2one('hospital.explanation')
    eprescription_id = fields.Many2one('hospital.eprescription')
    aciklama_turu = fields.Selection([
        ('1', 'Teşhis/Tanı'),
        ('2', 'Tedavi Süresi'),
        ('3', 'Hasta Güvenlik ve İzleme Formu'),
        ('4', 'Tetkik Sonucu'),
        ('5', 'Endikasyon Dışı Kullanım İzni'),
        ('99', 'Other')
    ], string="Açıklama Type")
    aciklama = fields.Text(string="E-Prescriptions Açıklaması")
