# -*- coding: utf8 -*-

#
#
# -*- Report Diagnostic List Sorgula Servisi -*-
#
#
import datetime

from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class TeshisListesiSorgula(models.Model):
    _name = "service.teshis_listesi"
    _description = "Report Diagnostic List Servisi"

    facility_code = fields.Char(string="Facility Code")
    doctor_id = fields.Many2one('podiatry.doctor', string="Doctor")

    teshis_ids = fields.Many2many(
        'podiatry.ereport.teshis', string="Diagnostic List")

    def teshis_listesi_sorgula(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiYardimciIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        vals = {
            'arg0': {
                'tesisKodu': int(self.facility_code),
                'doktorTcKimlikNo': int(self.doctor_id.doctor_tc)
            }
        }
        with client.settings(strict=False):
            teshis_listesi = client.service.raporTeshisListesiSorgula(**vals)
        result = teshis_listesi.raporTeshisListesi

        if teshis_listesi.sonucKodu == '0000':
            my_teshis_kod = self.env['podiatry.ereport.teshis'].search(
                []).mapped('rapor_teshis_kodu')
            not_in_my_teshis = filter(
                lambda r: r.raporTeshisKodu not in my_teshis_kod, result)
            for teshis in not_in_my_teshis:
                self.env['podiatry.ereport.teshis'].create({
                    'rapor_teshis_kodu': teshis.raporTeshisKodu,
                    'rapor_teshis_adi': teshis.aciklama
                })
                my_teshis = self.env['podiatry.ereport.teshis'].search(
                    [('rapor_teshis_kodu', '=', teshis.raporTeshisKodu)])

                self.teshis_ids = [(4, my_teshis.id, 0)]

            return {
                'name': 'Yeni Eklenen Teşhisler',
                'type': 'ir.actions.act_window',
                'res_model': 'podiatry.teshis.wizard',
                'target': 'new',
                'view_type': 'form',
                'view_mode': 'form',
                'context': {
                    'default_teshis_ids': [(4, teshis.id) for teshis in self.teshis_ids]
                }
            }
        else:
            return {
                'name': 'Sonuç Mesajı',
                'type': 'ir.actions.act_window',
                'res_model': 'sonuc.mesaji.wizard',
                'target': 'new',
                'view_mode': 'form',
                'context': {
                    'default_sonuc_kodu': teshis_listesi.sonucKodu,
                    'default_sonuc_mesaji': teshis_listesi.sonucMesaji,
                }
            }
