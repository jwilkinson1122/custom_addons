# -*- coding: utf8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EReport(models.Model):
    _name = "hospital.ereport"
    _description = "E-Report"
    _rec_name = 'rapor_no'

    tesis_kod = fields.Char(string="Facility Code", required=True)
    rapor_takip_no = fields.Char(
        string="ReportFollow up No")   # MEDULA uretecek
    # Sağlık tesisi uretecek
    protokol_no = fields.Char(string="Protocol No", required=True)
    takip_no = fields.Char(string="Takip No")  # MEDULA takip numarası

    patient_id = fields.Many2one('hospital.epatient', string="Patient")
    patient_name = fields.Char(
        string="Patient Name", related="patient_id.name")
    patient_surname = fields.Char(
        string="Patient Last Name", related="patient_id.surname")

    # Sağlık tesisi uretecek
    rapor_no = fields.Char(string="Report No", required=True)
    rapor_tarihi = fields.Date(
        string="Report Date", default=fields.Date.context_today, date_format="dd.MM.yyyy")
    rapor_duzenleme_turu = fields.Selection([
        ('1', 'Health Board Report'),
        ('2', 'Specialist Physician Report')
    ], string="Report Editing Type", required=True)
    rapor_onay_durumu = fields.Selection([
        ('1', 'Waiting for approval'),
        ('2', 'Approved')
    ], string="Report Approval Status", default='1')

    rapor_olusturan_doktor = fields.Many2one(
        'hospital.doctor', string="Doctor")
    doctor_name = fields.Char(
        string="Doctor Name", related="rapor_olusturan_doktor.name")
    doctor_surname = fields.Char(
        string="Doctor Last Name", related="rapor_olusturan_doktor.surname")

    rapor_teshis_listesi = fields.One2many(
        'ereport.teshis.line', 'ereport_id', string="E-Report Diagnostic List")
    rapor_doktor_listesi = fields.Many2many(
        'hospital.doctor', string="E-Report Doctor List")
    rapor_doktor_listesi2 = fields.One2many(
        'ereport.doctor.line', 'ereport_id', string="E-Report Doctor List")
    rapor_etkin_madde_listesi = fields.Many2many(
        'hospital.etkin_madde', string="E-Report Active Item List")
    rapor_aciklama_listesi = fields.One2many(
        'hospital.ereport.explanation', 'ereport_id', string="E-Report Description List")
    rapor_tani_listesi = fields.Many2many(
        'hospital.diagnosis', string="E-Report Condition List")
    rapor_ilave_deger_listesi2 = fields.One2many(
        'hospital.ereport.ilave_deger', 'ereport_id', string="E-Report Additional Value List")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('heyet_onayinda', 'Delegation Approval'),
        ('bashekim_onayinda', 'Doctor Approval'),
        ('onaylanmadi', 'Not Approved'),
        ('onaylandi', 'Approved'),
        ('deleted', 'E-Report Deleted'),
    ], default="draft", string="Durum")

    def send_to_confirmation(self):
        ereport = self.env['hospital.ereport'].search(
            [('rapor_no', '=', self.rapor_no)])

        ereport.state = 'heyet_onayinda'


class EreportDoctorLine(models.Model):
    _name = "ereport.doctor.line"

    ereport_id = fields.Many2one('hospital.ereport', string="E-Report")
    doctor_id = fields.Many2one('hospital.doctor', string="Doctor")
    name = fields.Char(string="Doctor name", related="doctor_id.name")
    surname = fields.Char(string="Doctor surname", related="doctor_id.surname")
    doctor_tc = fields.Char(string="Doctor Tc", related="doctor_id.doctor_tc")


# EraporTeshisDVO
class EreportTeshisLine(models.Model):

    _name = "ereport.teshis.line"

    ereport_id = fields.Integer()
    rapor_teshis_kodu = fields.Many2one(
        'hospital.ereport.teshis', string="Diagnostic Code")
    baslangic_tarihi = fields.Date(
        string="Start Date", date_format="dd.MM.yyyy")
    bitis_tarihi = fields.Date(string="End Date", date_format="dd.MM.yyyy")
    tani_listesi = fields.Many2many('hospital.diagnosis')
