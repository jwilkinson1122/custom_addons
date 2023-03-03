# -*- coding: utf8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EPrescriptions(models.Model):
    _name = "hospital.eprescription"
    _description = "E-Prescription"
    _rec_name = 'seri_no'

    doctor_id = fields.Many2one(
        'hospital.doctor', string="Doctor", required=True)
    doctor_name = fields.Char(string="Doctor Adı", related="doctor_id.name")
    doctor_surname = fields.Char(
        string="Doctor Last Name", related="doctor_id.surname")
    brans_kod = fields.Char(string="Branch Code",
                            related="doctor_id.brans_kod")

    patient_id = fields.Many2one(
        'hospital.epatient', string="Patient", required=True)
    patient_name = fields.Char(
        string="Patient Name", related="patient_id.name")
    patient_surname = fields.Char(
        string="Patient Surname", related="patient_id.surname")

    recete_tur = fields.Selection([
        ('1', 'Normal'),
        ('2', 'Rush'),
    ], string="Prescriptions Type", required=True)
    recete_alt_tur = fields.Selection([
        ('1', 'Custom'),
        ('2', 'OTC'),
        ('3', 'Brace'),
        ('4', 'Repair'),
    ], string="Prescriptions Alt Type", required=True)

    tesis_kod = fields.Char(string="Facility Code")
    takip_no = fields.Char(string="Takip No")
    provizyon_tip = fields.Selection([
        ('1', 'Normal'),
        ('2', 'Traffic'),
        ('3', 'Work Accident'),
        ('4', 'Condition'),
        ('5', 'Pregnant'),
        ('6', '3713/21')
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

    @api.model
    def _create(self, data_list):
        if self.env['hospital.eprescription'].search([('seri_no', '=', data_list[0]['stored']['seri_no'].strip())]):
            raise ValidationError(_("Bu reçete daha önce kaydedilmiş!"))
        return super(EPrescriptions, self)._create(data_list)


# İlaç ekle
class AppointmentPharmacyLines(models.Model):
    _name = "eprescription.pharmacy.lines2"
    _description = "E-Prescription Pharmacy Lines"

    product_id = fields.Many2one(
        "hospital.ilac", string="Barkod", required=True)
    medicine_name = fields.Char(
        string="Item Name", related="product_id.ilac_adi")
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

    explanation_line_ids = fields.One2many('eprescription.medicine.explanation.lines', 'pharmacy_line_id',
                                           string="İlaç Açıklama")
    erecete_ilac_aciklama_turu = fields.Selection([
        ('1', 'Teşhis/Tanı'),
        ('2', 'Tedavi Süresi'),
        ('3', 'Hasta Güvenlik ve İzleme Formu'),
        ('4', 'Tetkik Sonucu'),
        ('5', 'Endikasyon Dışı Kullanım İzni'),
        ('99', 'Other')
    ], string="E-Prescriptions İlaç Açıklama Type")
    erecete_ilac_aciklama = fields.Text(string="E-Prescriptions İlaç Açıklama")

    eprescription_id = fields.Many2one(
        'hospital.eprescription', ondelete="cascade")
    # sub_total = fields.Float(string="Total", compute="_compute_sub_total")


# E-Prescriptions Add Description
class EprescriptionsExplanationLines(models.Model):
    _name = "eprescription.explanation.lines"
    _description = "E-Prescription Explanation Lines"

    eprescription_id = fields.Many2one('hospital.eprescription')
    service_exp_id = fields.Many2one('hospital.service.add.explanation')
    aciklama_turu = fields.Selection([
        ('1', 'Teşhis/Tanı'),
        ('2', 'Tedavi Süresi'),
        ('3', 'Hasta Güvenlik ve İzleme Formu'),
        ('4', 'Tetkik Sonucu'),
        ('5', 'Endikasyon Dışı Kullanım İzni'),
        ('99', 'Other')
    ], string="Açıklama Type")
    aciklama = fields.Text(string="E-Prescriptions Açıklaması")


class EprescriptionsMedicineExplanationLines(models.Model):
    _name = "eprescription.medicine.explanation.lines"
    _description = "E-Prescription Medicine Explanation Lines"

    pharmacy_line_id = fields.Many2one('eprescription.pharmacy.lines2')
    service_medicine_exp_id = fields.Many2one(
        'hospital.service.add.medicine.explanation')
    aciklama_turu = fields.Selection([
        ('1', 'Teşhis/Tanı'),
        ('2', 'Tedavi Süresi'),
        ('3', 'Hasta Güvenlik ve İzleme Formu'),
        ('4', 'Tetkik Sonucu'),
        ('5', 'Endikasyon Dışı Kullanım İzni'),
        ('99', 'Other')
    ], string="Açıklama Type")
    aciklama = fields.Text(string="E-Prescriptions Açıklaması")

# KULLANILMIYOR!!!


class AppointmentPharmacyLines2(models.Model):
    _name = "eprescription.pharmacy.lines"
    _description = "E-Prescription Pharmacy Lines"
