# -*- coding: utf8 -*-

#
#
# -*- E-Report Teşhis Ekleme Servisi -*-
#
#
import datetime

from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class AddEreportTeshis(models.Model):
    _name = "podiatry.service.add.ereport.teshis"

    ereport_id = fields.Integer()
    doctor_id = fields.Many2one('podiatry.doctor', string="Doctor")
    # teshis_lines = fields.One2many('ereport.add.teshis.line', 'service_add_ereport_teshis', string="Diagnostic List")
    teshis_lines = fields.Many2many('podiatry.ereport.teshis')
    teshis_lines2 = fields.One2many(
        'ereport.teshis.line', 'ereport_id', string="Teshis Listesi")
    teshis_tani = fields.Many2many(
        'podiatry.diagnosis', string="Teşhis Tanıları")

    def add_teshis(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiRaporIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        ereport = self.env['podiatry.ereport'].search(
            [('id', '=', self.ereport_id)])

        tani_list = []
        for tani in self.teshis_tani:
            tani_list.append({
                'kodu': tani.tani_kodu,
                'adi': tani.tani_adi
            })

        teshis_list = []
        for new_teshis in self.teshis_lines2:

            teshis_list.append({
                'raporTeshisKodu': new_teshis.rapor_teshis_kodu.rapor_teshis_kodu,
                'baslangicTarihi': str(new_teshis.baslangic_tarihi.day) + '.' + str(
                    new_teshis.baslangic_tarihi.month) + '.' + str(new_teshis.baslangic_tarihi.year),
                'bitisTarihi': str(new_teshis.bitis_tarihi.day) + '.' + str(
                    new_teshis.bitis_tarihi.month) + '.' + str(new_teshis.bitis_tarihi.year),
                'taniListesi': tani_list
            })

        vals = {
            'arg0': {
                'raporTakipNo': ereport.report_follow_no,
                'tesisKodu': ereport.facility_code,
                'doktorTcKimlikNo': self.doctor_id.doctor_tc,
                'eraporTeshisDVO': teshis_list
            }
        }

        with client.settings(strict=False):
            erapor = client.service.eraporTeshisEkle(**vals)

        if erapor.sonucKodu == '0000':
            # model = self._context.get('active_model')
            # active_id = self._context.get('active_id')
            ereport.rapor_teshis_listesi = [(0, 0, {
                'rapor_teshis_kodu': self.env['podiatry.ereport.teshis']
                                             .search([('rapor_teshis_kodu', '=', int(teshis.rapor_teshis_kodu.rapor_teshis_kodu))]).id,
                                             'baslangic_tarihi': teshis.baslangic_tarihi,
                                             'bitis_tarihi': teshis.bitis_tarihi,
                                             'tani_listesi': [(4, tani.id,) for tani in self.teshis_tani]
                                             }) for teshis in self.teshis_lines2]
            # active_model_id = self.env[model].browse(active_id)

        return {
            'name': 'Sonuç Mesajı',
            'type': 'ir.actions.act_window',
            'res_model': 'sonuc.mesaji.wizard',
            'target': 'new',
            'view_mode': 'form',
            'context': {
                'default_sonuc_kodu': erapor.sonucKodu,
                'default_sonuc_mesaji': erapor.sonucMesaji if erapor.sonucKodu != '0000' else 'İşlem Başarılı!',
            }
        }


class EreportAddTeshisLine(models.Model):
    _name = "ereport.add.teshis.line"

    service_add_ereport_teshis = fields.Many2one(
        'podiatry.service.add.ereport.teshis')
    rapor_teshis_kodu = fields.Many2one(
        'podiatry.ereport.teshis', string="Diagnostic Code")
    baslangic_tarihi = fields.Date(
        string="Start Date", date_format="dd.MM.yyyy")
    bitis_tarihi = fields.Date(string="End Date", date_format="dd.MM.yyyy")
    tani_listesi = fields.Many2many(
        'podiatry.diagnosis', string="Condition List")


class EreportAddTeshisTaniLine(models.Model):
    _name = "ereport.add.teshis.tani.line"

    tani_id = fields.Many2one('podiatry.diagnosis')
    tani_kodu = fields.Char(string="Tanı Kodu", related="tani_id.tani_kodu")
    tani_adi = fields.Char(string="Tanı Adı", related="tani_id.tani_adi")
