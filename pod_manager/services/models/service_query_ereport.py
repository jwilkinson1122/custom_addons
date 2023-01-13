# -*- coding: utf8 -*-

#
#
# -*- E-Report Sorgula Servisi -*-
#
#
import datetime

from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class QueryEreport(models.Model):
    _name = "podiatry.service.query.ereport"
    _description = "Podiatry Query E-Report Service"

    report_follow_no = fields.Char(string="E-ReportFollow up No")
    facility_code = fields.Char(string="Facility Code")
    doctor_id = fields.Many2one('podiatry.doctor', string="Doctor")

    def query_ereport(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiRaporIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        ereport = self.env['podiatry.ereport'].search(
            [('report_follow_no', '=', self.report_follow_no)])

        vals = {
            'arg0': {
                'tesisKodu': self.facility_code,
                'raporTakipNo': self.report_follow_no,
                'doktorTcKimlikNo': self.doctor_id.doctor_tc
            }
        }
        with client.settings(strict=False):
            erapor = client.service.eraporSorgula(**vals)
        result = erapor.eraporDVO

        if erapor.sonucKodu == '0000':

            aciklama_listesi = []
            for aciklama in result.eraporAciklamaListesi:
                aciklama_listesi.append({
                    'aciklama': aciklama.aciklama,
                    'takip_formu_no': aciklama.takipFormuNo
                })

            doktor_listesi = []
            for doktor in result.eraporDoktorListesi:
                # doktor = self.env['podiatry.doctor'].search([('')])
                doktor_listesi.append({
                    'doctor_tc': doktor.tcKimlikNo,
                    'brans_kod': doktor.bransKodu,
                    'sertifika_kod': doktor.sertifikaKodu,
                    'name': doktor.adi,
                    'surname': doktor.soyadi
                })

            etkin_madde_listesi = []
            for etkin_madde in result.eraporEtkinMaddeListesi:
                etkin_madde_listesi.append({
                    'etkin_maddedvo_id': self.env['podiatry.etkin_maddedvo'].search([('etkin_madde_kodu', '=', etkin_madde['etkinMaddeDVO'].kodu)]).id,
                    'etkin_madde_kodu': etkin_madde.etkinMaddeKodu,
                    'kullanim_doz1': etkin_madde.kullanimDoz1,
                    'kullanim_doz2': etkin_madde.kullanimDoz2,
                    'kullanim_doz_birimi': etkin_madde.kullanimDozBirimi,
                    'kullanim_doz_periyot': etkin_madde.kullanimDozPeriyot,
                    'kullanim_doz_periyot_birimi': etkin_madde.kullanimDozPeriyotBirimi
                })

            ilave_deger_listesi = []
            for ilave_deger in result.eraporIlaveDegerListesi:
                ilave_deger_listesi.append({
                    'turu': str(ilave_deger.turu) if ilave_deger.turu else '',
                    'deger': ilave_deger.degeri if ilave_deger.degeri else '',
                    'aciklama': ilave_deger.aciklama if ilave_deger.aciklama else ''
                })

            tani_listesi = []
            for tani in result.eraporTaniListesi:
                tani_listesi.append({
                    'tani_adi': tani.taniAdi,
                    'tani_kodu': tani.taniKodu
                })

            teshis_listesi = []
            teshis_tani_listesi = []
            for teshis in result.eraporTeshisListesi:
                for teshis_tani in teshis.taniListesi:
                    if teshis_tani.kodu != None:
                        teshis_tani_listesi.append({
                            'tani_kodu': teshis_tani.kodu,
                            'tani_adi': teshis_tani.adi
                        })
                teshis_listesi.append({
                    'rapor_teshis_kodu': self.env['podiatry.ereport.teshis'].search([('rapor_teshis_kodu', '=', str(teshis.raporTeshisKodu))], limit=1).id,
                    'baslangic_tarihi': datetime.datetime.strptime(teshis.baslangicTarihi, "%d.%m.%Y"),
                    'bitis_tarihi': datetime.datetime.strptime(teshis.bitisTarihi, "%d.%m.%Y"),
                    'tani_listesi': teshis_tani_listesi
                })

            return {
                'name': 'Sorgu Sonucu',
                'type': 'ir.actions.act_window',
                'res_model': 'podiatry.ereport.wizard',
                'target': 'new',
                'view_type': 'form',
                'view_mode': 'form',
                'context': {
                    'default_rapor_tarihi': datetime.datetime.strptime(result.raporTarihi, "%d.%m.%Y"),
                    'default_protokol_no': result.protokolNo,
                    'default_takipNo': result.takipNo,
                    'default_report_follow_no': result.raporTakipNo,
                    'default_tesis_kod': result.tesisKodu,
                    'default_rapor_no': result.raporNo.strip(),
                    'default_rapor_duzenleme_turu': result.raporDuzenlemeTuru,
                    'default_rapor_onay_durumu': result.raporOnayDurumu,
                    'default_rapor_olusturan_doktor': ereport.rapor_olusturan_doktor.id,
                    'default_patient_id': self.env['podiatry.patient'].search([('tc_no', '=', result.hastaTcKimlikNo)], limit=1).id,
                    'default_rapor_teshis_listesi': [(4, teshis.id) for teshis in ereport.rapor_teshis_listesi],
                    'default_rapor_doktor_listesi': [(4, doctor.id) for doctor in ereport.rapor_doktor_listesi],
                    'default_rapor_etkin_madde_listesi': [(4, etkin_madde.id) for etkin_madde in ereport.rapor_etkin_madde_listesi],
                    'default_rapor_aciklama_listesi': [(4, aciklama.id) for aciklama in ereport.rapor_aciklama_listesi],
                    'default_rapor_tani_listesi': [(4, tani.id) for tani in ereport.rapor_tani_listesi],
                    'default_rapor_ilave_deger_listesi2': [(4, ilave_deger.id) for ilave_deger in ereport.rapor_ilave_deger_listesi2]
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
                    'default_sonuc_kodu': erapor.sonucKodu,
                    'default_sonuc_mesaji': erapor.sonucMesaji,
                }
            }
