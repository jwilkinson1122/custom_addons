# -*- coding: utf8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Prescriptions(models.Model):
    _name = "podiatry.prescription"
    _description = "Prescription"
    _rec_name = 'reference_no'

    practice_id = fields.Many2one(
        'podiatry.practice', string="Practice", required=True)
    doctor_id = fields.Many2one(
        'podiatry.doctor', string="Doctor", required=True)
    doctor_name = fields.Char(string="Doctor Adı", related="doctor_id.name")
    doctor_surname = fields.Char(
        string="Doctor Last Name", related="doctor_id.surname")
    brans_kod = fields.Char(string="Branch Code",
                            related="doctor_id.brans_kod")

    patient_id = fields.Many2one(
        'podiatry.patient', string="Patient", required=True)
    patient_name = fields.Char(
        string="Patient Name", related="patient_id.name")
    patient_surname = fields.Char(
        string="Patient Surname", related="patient_id.surname")

    recete_tur = fields.Selection([
        ('1', 'Normal'),
        ('2', 'Rush'),
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
        ('2', 'Traffic'),
        ('3', 'Work Accident'),
        ('4', 'Condition'),
        ('5', 'Pregnant'),
        ('6', '3713/21')
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
        'podiatry.diagnosis', string="Diagnosis", required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Complete'),
        ('deleted', 'Prescriptions Deleted')
    ], default="draft", string="Durum")

    @api.model
    def _create(self, data_list):
        if self.env['podiatry.prescription'].search([('reference_no', '=', data_list[0]['stored']['reference_no'].strip())]):
            raise ValidationError(_("Bu reçete daha önce kaydedilmiş!"))
        return super(Prescriptions, self)._create(data_list)


# İlaç ekle
class AppointmentPharmacyLines(models.Model):
    _name = "prescription.pharmacy.lines2"
    _description = "Prescription Pharmacy Lines"

    product_id = fields.Many2one(
        "podiatry.ilac", string="Barkod", required=True)
    medicine_name = fields.Char(
        string="Product Name", related="product_id.ilac_adi")
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

    explanation_line_ids = fields.One2many('prescription.medicine.explanation.lines', 'pharmacy_line_id',
                                           string="Product")
    erecete_ilac_aciklama_turu = fields.Selection([
        ('1', 'Teşhis/Tanı'),
        ('2', 'Tedavi Süresi'),
        ('3', 'Hasta Güvenlik ve İzleme Formu'),
        ('4', 'Tetkik Sonucu'),
        ('5', 'Endikasyon Dışı Kullanım İzni'),
        ('99', 'Other')
    ], string="Prescriptions Product Type")
    erecete_ilac_aciklama = fields.Text(string="Prescriptions Product")

    prescription_id = fields.Many2one(
        'podiatry.prescription', ondelete="cascade")
    # sub_total = fields.Float(string="Total", compute="_compute_sub_total")


# Prescriptions Add Description
class PrescriptionsExplanationLines(models.Model):
    _name = "prescription.explanation.lines"
    _description = "Prescription Explanation Lines"

    prescription_id = fields.Many2one('podiatry.prescription')
    service_exp_id = fields.Many2one('podiatry.service.add.explanation')
    aciklama_turu = fields.Selection([
        ('1', 'Teşhis/Tanı'),
        ('2', 'Tedavi Süresi'),
        ('3', 'Hasta Güvenlik ve İzleme Formu'),
        ('4', 'Tetkik Sonucu'),
        ('5', 'Endikasyon Dışı Kullanım İzni'),
        ('99', 'Other')
    ], string="Açıklama Type")
    aciklama = fields.Text(string="Prescriptions Açıklaması")


class PrescriptionsMedicineExplanationLines(models.Model):
    _name = "prescription.medicine.explanation.lines"
    _description = "Prescription Medicine Explanation Lines"

    pharmacy_line_id = fields.Many2one('prescription.pharmacy.lines2')
    service_medicine_exp_id = fields.Many2one(
        'podiatry.service.add.medicine.explanation')
    aciklama_turu = fields.Selection([
        ('1', 'Teşhis/Tanı'),
        ('2', 'Tedavi Süresi'),
        ('3', 'Hasta Güvenlik ve İzleme Formu'),
        ('4', 'Tetkik Sonucu'),
        ('5', 'Endikasyon Dışı Kullanım İzni'),
        ('99', 'Other')
    ], string="Açıklama Type")
    aciklama = fields.Text(string="Prescriptions Açıklaması")

# KULLANILMIYOR!!!


class AppointmentPharmacyLines2(models.Model):
    _name = "prescription.pharmacy.lines"
    _description = "Prescription Pharmacy Lines"
