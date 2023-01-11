# -*- coding: utf8 -*-
import dateutil.utils

from odoo import models, fields, api


class EReportIlaveDeger(models.Model):
    _name = "podiatry.ereport.ilave_deger"
    _description = "Hospital E-Report İlave Değer"

    ereport_id = fields.Many2one('podiatry.ereport')
    turu = fields.Selection([
        ('1', 'Report Düzenleme Nedeni'),
        ('2', 'Kilo'),
        ('3', 'Hemoglobin A1c'),
        ('4', 'Açlık Kan Şekeri'),
        ('5', 'Karaciğer Nakilli Hasta (Yüksek Riskli)'),
        ('6', 'Karaciğer Nakilli Hasta (Düşük Riskli)'),
        ('7', 'ECOG Performans Skoru'),
        ('8', 'EGFR, ALK, ROS Mutasyonu ve/veya Semptomatik Beyin Metastazı Olmayan Hasta'),
        ('9', 'Bir Basamak Kemoterapi Tedavisi Almış ve Sonrasında Progresyon Gelişmiş Olan Hasta'),
        ('10', 'Lokal İleri ve/veya Metastatik Küçük Hücreli Dışı Akciğer Kanseri Olan Hasta'),
        ('11', 'Hiperamonyemi'),
        ('12', 'Günlük Kalori Miktarı')
    ], string="İlave Değer Type")

    deger = fields.Char(string="Değer")

    rapor_duzenleme_nedeni = fields.Selection([
        ('1', 'Yaş'),
        ('2', 'Doz'),
        ('3', 'Cinsiyet'),
        ('4', 'Endikasyon'),
        ('5', 'SUT Kuralı')
    ], string="Report Düzenleme Nedeni")

    kilo = fields.Float(string="Kilo")
    hemoglobin = fields.Float(string="Hemoglobin A1c")
    kan_sekeri = fields.Float(string="Açlık Kan Şekeri")
    karaciger_nakilli_hasta_YR = fields.Selection([
        ('1', 'Karaciğer nakli öncesi HBV DNA pozitif olan'),
        ('2', 'Karaciğer nakli öncesi HBeAg pozitif olan'),
        ('3', 'Karaciğer nakli öncesi hepatoselüler kanseri bulunan'),
        ('4', 'Delta virüs veya HIV ile ko-enfekte olan '),
        ('5', 'Karaciğer nakli öncesi antiviral tedaviye direnç öyküsü ya da uyumsuzluğu olan'),
        ('6', 'Delta virüs veya HIV ile ko-enfekte olan (2009 yılı öncesi nakil olan hasta)'),
    ], string="Karaciğer Nakilli Hasta (Yüksek Riskli)")
    karaciger_nakilli_hasta_DR = fields.Selection([
        ('1', 'Karaciğer nakli öncesi HBV DNA negatif olan')
    ], default='1', readonly=True, string="Karaciğer Nakilli Hasta (Düşük Riskli)")
    ECOG = fields.Selection([
        ('0', 'ECOG Performans Skoru 0 Olan Hasta'),
        ('1', 'ECOG Performans Skoru 1 Olan Hasta')
    ], string="ECOG Performans Skoru")

    # EGFR, ALK, ROS Mutasyonu ve/veya Semptomatik Beyin Metastazı Olmayan Hasta
    EGFR = fields.Char(default='1', readonly=True,
                       string="EGFR, ALK, ROS Mutasyonu ve/veya Semptomatik Beyin Metastazı Olmayan Hasta")

    # Bir Basamak Kemoterapi Tedavisi Almış ve Sonrasında Progresyon Gelişmiş Olan Hasta
    progresyon = fields.Char(default='1', readonly=True,
                             string="Bir Basamak Kemoterapi Tedavisi Almış ve Sonrasında Progresyon Gelişmiş Olan Hasta")

    # Lokal İleri ve/veya Metastatik Küçük Hücreli Dışı Akciğer Kanseri Olan Hasta
    akciger_kanseri = fields.Char(default='1', readonly=True,
                                  string="Lokal İleri ve/veya Metastatik Küçük Hücreli Dışı Akciğer Kanseri Olan Hasta")
    Hiperamonyemi = fields.Char(default='1', readonly=True)

    gunluk_kalori = fields.Float(string="Günlük Kalori Miktarı")

    aciklama = fields.Text(string="Açıklama")

    @api.onchange('turu')
    def deneme(self):
        self.deger = '1'

    @api.onchange('rapor_duzenleme_nedeni')
    def test(self):
        self.deger = self.rapor_duzenleme_nedeni

    @api.onchange('kilo')
    def test1(self):
        self.deger = str(self.kilo)

    @api.onchange('hemoglobin')
    def test2(self):
        self.deger = str(self.hemoglobin)

    @api.onchange('kan_sekeri')
    def test3(self):
        self.deger = str(self.kan_sekeri)

    @api.onchange('karaciger_nakilli_hasta_YR')
    def test4(self):
        self.deger = self.karaciger_nakilli_hasta_YR

    @api.onchange('karaciger_nakilli_hasta_DR')
    def test5(self):
        self.deger = '1'

    @api.onchange('ECOG')
    def test6(self):
        self.deger = self.ECOG

    @api.onchange('EGFR')
    def test7(self):
        self.deger = '1'

    @api.onchange('progresyon')
    def test8(self):
        self.deger = '1'

    @api.onchange('akciger_kanseri')
    def test9(self):
        self.deger = '1'

    @api.onchange('Hiperamonyemi')
    def test10(self):
        self.deger = '1'

    @api.onchange('gunluk_kalori')
    def test11(self):
        self.deger = str(self.gunluk_kalori)
