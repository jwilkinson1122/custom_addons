# -*- coding: utf8 -*-

from odoo import models, fields, api


class EReportWizard(models.TransientModel):
    _name = "podiatry.ereport.wizard"
    _description = "E-Report Wizard"

    facility_code = fields.Char(string="Facility Code", required=True)
    report_follow_no = fields.Char(
        string="ReportFollow up No")   # MEDULA uretecek
    # Sağlık tesisi uretecek
    protokol_no = fields.Char(string="Protocol No", required=True)
    tracking_no = fields.Char(string="Tracking No")  # MEDULA takip numarası

    patient_id = fields.Many2one('podiatry.patient', string="Hasta")
    patient_name = fields.Char(string="Hasta Adı", related="patient_id.name")
    patient_surname = fields.Char(
        string="Hasta Last Name", related="patient_id.surname")

    # Sağlık tesisi uretecek
    report_no = fields.Char(string="Report No", required=True)
    rapor_tarihi = fields.Date(
        string="Report Date", default=fields.Date.context_today, date_format="dd.MM.yyyy")
    rapor_duzenleme_turu = fields.Selection([
        ('1', 'Sağlık Kurulu Raporu'),
        ('2', 'Uzman Hekim Raporu')
    ], string="Report Düzenleme Type", required=True)
    rapor_onay_durumu = fields.Selection([
        ('1', 'Onay Bekliyor'),
        ('2', 'Approved')
    ], string="Report Onay Durumu", required=True)

    rapor_olusturan_doktor = fields.Many2one(
        'podiatry.doctor', string="Raporu Oluşturan Doctor")

    rapor_teshis_listesi = fields.One2many(
        'ereport.teshis.line', 'ereport_id', string="E-Report Diagnostic List")
    rapor_doktor_listesi = fields.Many2many(
        'podiatry.doctor', string="E-Report Doctor List")
    rapor_etkin_madde_listesi = fields.Many2many(
        'podiatry.etkin_madde', string="E-Report Active Item List")
    rapor_aciklama_listesi = fields.One2many(
        'podiatry.ereport.explanation', 'ereport_id', string="E-Report Description List")
    rapor_tani_listesi = fields.Many2many(
        'podiatry.diagnosis', string="E-Report Condition List")
    rapor_ilave_deger_listesi2 = fields.One2many(
        'podiatry.ereport.ilave_deger', 'ereport_id', string="E-Report Additional Value List")
