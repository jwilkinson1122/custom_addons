# -*- coding: utf8 -*-

#
#
# -*- Normal Prescriptions ile Kaydedilebilen Product List Servisi -*-
#
#
import datetime

from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class NormalReceteIlacListesiSorgula(models.Model):
    _name = "service.normal_ilac_listesi"
    _description = "Normal Prescriptions İle Kaydedilebilen Product List Servisi"

    facility_code = fields.Char(string="Facility Code")
    doctor_id = fields.Many2one('podiatry.doctor', string="Doctor")
    islem_tarihi = fields.Date(string="İşlem Date", default=fields.Date.context_today, date_format="dd.MM.yyyy",
                               readonly=True)
    ilac_listesi = fields.Many2many('podiatry.ilac', string="Product List")

    def normal_ilac_listesi_sorgula(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiYardimciIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        vals = {
            'arg0': {
                'tesisKodu': int(self.facility_code),
                'doktorTcKimlikNo': int(self.doctor_id.doctor_id),
                'islemTarihi': str(self.islem_tarihi.day) + '.' + str(self.islem_tarihi.month) + '.' + str(
                    self.islem_tarihi.year)
            }
        }
        with client.settings(strict=False):
            ilac_listesi = client.service.normalReceteIlacListesiSorgula(
                **vals)
        result = ilac_listesi.ilacListesi

        if ilac_listesi.sonucKodu == '0000':
            my_ilac_barcode = self.env['podiatry.ilac'].search(
                []).mapped('barcode')
            not_in_my_ilac = filter(lambda r: str(
                r.barkod) not in my_ilac_barcode, result)
            for ilac in not_in_my_ilac:
                self.env['podiatry.ilac'].create({
                    'barcode': str(ilac.barkod),
                    'ilac_adi': ilac.ilacAdi,
                    'sgk_ilac_kodu': str(ilac.sgkIlacKodu),
                    'ambalaj_miktari': ilac.ambalajMiktari,
                    'tek_doz_miktari': ilac.tekDozMiktari,
                    'kutu_birim_miktari': ilac.kutuBirimMiktari,
                    'ayaktan_odenme_sarti': ilac.ayaktanOdenmeSarti,
                    'yatan_odenme_sarti': ilac.yatanOdenmeSarti,
                    'etkin_madde_kodu': ilac.etkinMaddeKodu
                })
                my_ilac = self.env['podiatry.ilac'].search(
                    [('barcode', '=', str(ilac.barkod))])

                self.ilac_listesi = [(4, my_ilac.id, 0)]

            return {
                'name': 'Yeni Eklenen Product',
                'type': 'ir.actions.act_window',
                'res_model': 'podiatry.ilac.wizard',
                'target': 'new',
                'view_type': 'form',
                'view_mode': 'form',
                'context': {
                    'default_ilac_listesi': [(4, ilac.id) for ilac in self.ilac_listesi]
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
                    'default_sonuc_kodu': ilac_listesi.sonucKodu,
                    'default_sonuc_mesaji': ilac_listesi.sonucMesaji,
                }
            }
