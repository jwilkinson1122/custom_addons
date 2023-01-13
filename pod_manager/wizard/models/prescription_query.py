# -*- coding: utf8 -*-

from odoo import models, fields, api


class Prescriptions(models.TransientModel):
    _name = "podiatry.prescription.query.wizard"
    _description = "Prescription wizard"

    doctor_id = fields.Many2one(
        'podiatry.doctor', string="Doctor", required=True)
    brans_kod = fields.Char(string="Branch Code",
                            related="doctor_id.brans_kod")

    patient_id = fields.Many2one(
        'podiatry.patient', string="Patient", required=True)
    patient_name = fields.Char(string="Hasta Ad", related="patient_id.name")
    patient_surname = fields.Char(
        string="Hasta Soyad", related="patient_id.surname")

    recete_tur = fields.Integer(string="Prescription Type", required=True)
    recete_alt_tur = fields.Integer(
        string="Device Type", required=True)

    rush_order = fields.Boolean('Rush Order')
    make_quantity = fields.Boolean('Qty to make')
    make_from_prior_rx = fields.Boolean('Make from prior rx')
    ship_to_patient = fields.Boolean('Ship to patient')
    make_left_only = fields.Boolean('Make left device only')
    make_right_only = fields.Boolean('Make right device only')
    make_bilateral = fields.Boolean('Make left / right pair')

    facility_code = fields.Char(string="Facility Code")
    tracking_no = fields.Char(string="Tracking No")
    provizyon_tip = fields.Integer(string="Provision Type")
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


# İlaç ekle
class AppointmentPharmacyLines(models.TransientModel):
    _name = "prescription.pharmacy.lines.wizard"
    _description = "Prescription Pharmacy Lines"

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
    ], string="Prescriptions Product Type")
    erecete_ilac_aciklama = fields.Text(string="Prescriptions Product")

    prescription_id = fields.Many2one('podiatry.prescription')
    # sub_total = fields.Float(string="Total", compute="_compute_sub_total")


# Prescriptions Add Description
class PrescriptionsExplanationLines(models.TransientModel):
    _name = "prescription.explanation.lines.wizard"
    _description = "Prescription Explanation Lines"

    explanation_id = fields.Many2one('podiatry.explanation')
    prescription_id = fields.Many2one('podiatry.prescription')
    aciklama_turu = fields.Selection([
        ('1', 'Teşhis/Tanı'),
        ('2', 'Tedavi Süresi'),
        ('3', 'Hasta Güvenlik ve İzleme Formu'),
        ('4', 'Tetkik Sonucu'),
        ('5', 'Endikasyon Dışı Kullanım İzni'),
        ('99', 'Other')
    ], string="Açıklama Type")
    aciklama = fields.Text(string="Prescriptions Açıklaması")
