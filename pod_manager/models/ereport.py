# -*- coding: utf8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EReport(models.Model):
    _name = "podiatry.ereport"
    _description = "E-Report"
    _rec_name = 'report_no'

    facility_code = fields.Char(string="Facility Code", required=True)
    report_follow_no = fields.Char(
        string="ReportFollow up No")   # MEDULA uretecek
    # Sağlık tesisi uretecek
    protokol_no = fields.Char(string="Protocol No", required=True)
    tracking_no = fields.Char(string="Tracking No")  # MEDULA takip numarası
    patient_id = fields.Many2one('podiatry.patient', string="Patient")
    patient_name = fields.Char(
        string="Patient Name", related="patient_id.name")
    patient_surname = fields.Char(
        string="Patient Last Name", related="patient_id.surname")
    # Sağlık tesisi uretecek
    report_no = fields.Char(string="Report No", required=True)
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
        'podiatry.doctor', string="Doctor")
    doctor_name = fields.Char(string="Doctor Name",
                              related="rapor_olusturan_doktor.name")
    doctor_surname = fields.Char(
        string="Doctor Last Name", related="rapor_olusturan_doktor.surname")

    rapor_teshis_listesi = fields.One2many(
        'ereport.teshis.line', 'ereport_id', string="E-Report Diagnostic List")
    rapor_doktor_listesi = fields.Many2many(
        'podiatry.doctor', string="E-Report Doctor List")
    rapor_doktor_listesi2 = fields.One2many(
        'ereport.doctor.line', 'ereport_id', string="E-Report Doctor List")
    rapor_etkin_madde_listesi = fields.Many2many(
        'podiatry.etkin_madde', string="E-Report Active Item List")
    rapor_aciklama_listesi = fields.One2many(
        'podiatry.ereport.explanation', 'ereport_id', string="E-Report Description List")
    rapor_tani_listesi = fields.Many2many(
        'podiatry.diagnosis', string="E-Report Condition List")
    rapor_ilave_deger_listesi2 = fields.One2many(
        'podiatry.ereport.ilave_deger', 'ereport_id', string="E-Report Additional Value List")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('heyet_onayinda', 'Delegation Approval'),
        ('bashekim_onayinda', 'Doctor Approval'),
        ('onaylanmadi', 'Not Approved'),
        ('onaylandi', 'Approved'),
        ('deleted', 'E-Report Deleted'),
    ], default="draft", string="Durum")

    def send_to_confirmation(self):
        ereport = self.env['podiatry.ereport'].search(
            [('report_no', '=', self.report_no)])

        ereport.state = 'heyet_onayinda'


class EreportDoctorLine(models.Model):
    _name = "ereport.doctor.line"

    ereport_id = fields.Many2one('podiatry.ereport', string="E-Report")
    doctor_id = fields.Many2one('podiatry.doctor', string="Doctor")
    name = fields.Char(string="Doctor name", related="doctor_id.name")
    surname = fields.Char(string="Doctor surname", related="doctor_id.surname")
    # doctor_id = fields.Many2many(
    #     string="Doctor ID", related="doctor_id.doctor_id")


# EraporTeshisDVO
class EreportTeshisLine(models.Model):

    _name = "ereport.teshis.line"

    ereport_id = fields.Integer()
    rapor_teshis_kodu = fields.Many2one(
        'podiatry.ereport.teshis', string="Diagnostic Code")
    baslangic_tarihi = fields.Date(
        string="Start Date", date_format="dd.MM.yyyy")
    bitis_tarihi = fields.Date(string="End Date", date_format="dd.MM.yyyy")
    tani_listesi = fields.Many2many('podiatry.diagnosis')
