# -*- coding: utf8 -*-

#
#
# -*- E-Report Giriş Servisi -*-
#
#


from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class SaveEreport(models.Model):
    _name = "podiatry.service.save.ereport"
    _description = "Podiatry E-Report Save Service"

    ereport_id = fields.Integer()

    def save_ereport(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiRaporIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        ereport = self.env['podiatry.ereport'].search(
            [('id', '=', self.ereport_id)])
        rapor_olusturan_doktor = self.env['podiatry.doctor'].search(
            [('id', '=', ereport.rapor_olusturan_doktor.id)])
        patient = self.env['podiatry.patient'].search(
            [('id', '=', ereport.patient_id.id)])

        teshis_listesi = []
        teshis_tani_listesi = []

        for teshis in ereport.rapor_teshis_listesi:
            for tani in teshis.tani_listesi:
                teshis_tani_listesi.append({
                    'kodu': tani.tani_kodu.strip(),
                    'adi': tani.tani_adi.strip()
                })
            teshis_listesi.append({
                'raporTeshisKodu': teshis.rapor_teshis_kodu.rapor_teshis_kodu,
                'baslangicTarihi': str(teshis.baslangic_tarihi.day) + '.' + str(
                    teshis.baslangic_tarihi.month) + '.' + str(teshis.baslangic_tarihi.year),
                'bitisTarihi': str(teshis.bitis_tarihi.day) + '.' + str(teshis.bitis_tarihi.month) + '.' + str(
                    teshis.bitis_tarihi.year),
                'taniListesi': teshis_tani_listesi
            })

        doktor_listesi = []

        for doktor in ereport.rapor_doktor_listesi:
            doktor_listesi.append({
                'tcKimlikNo': doktor.doctor_id if doktor.doctor_id else '',
                'bransKodu': doktor.practice_id.strip() if doktor.practice_id else '',
                'sertifikaKodu': doktor.sertifika_kod if doktor.sertifika_kod else '',
                'adi': doktor.name.strip() if doktor.name else '',
                'soyadi': doktor.surname.strip() if doktor.surname else ''
            })

        etkin_madde_listesi = []
        for etkin_madde in ereport.rapor_etkin_madde_listesi:
            etkin_maddedvo = self.env['podiatry.etkin_maddedvo'].search(
                [('id', '=', etkin_madde.etkin_maddedvo_id.id)])
            etkin_madde_listesi.append({
                'etkinMaddeKodu': etkin_madde.etkin_madde_kodu,
                'kullanimDoz1': etkin_madde.kullanim_doz1,
                'kullanimDoz2': etkin_madde.kullanim_doz2,
                'kullanimDozBirimi': etkin_madde.kullanim_doz_birimi.strip(),
                'kullanimDozPeriyot': etkin_madde.kullanim_doz_periyot,
                'kullanimDozPeriyotBirimi': etkin_madde.kullanim_doz_periyot_birimi.strip(),
                'etkinMaddeDVO': {
                    'kodu': etkin_maddedvo.etkin_madde_kodu.strip(),
                    'adi': etkin_maddedvo.etkin_madde_adi.strip(),
                    'icerikMiktari': str(etkin_maddedvo.etkin_madde_icerik_miktari),
                    'formu': etkin_maddedvo.etkin_madde_formu.strip()
                }
            })

        aciklama_listesi = []
        for aciklama in ereport.rapor_aciklama_listesi:
            aciklama_listesi.append({
                'aciklama': aciklama.aciklama.strip(),
                'takipFormuNo': aciklama.takip_formu_no.strip()
            })

        tani_listesi = []
        for tani in ereport.rapor_tani_listesi:
            tani_listesi.append({
                'taniAdi': tani.tani_adi.strip(),
                'taniKodu': tani.tani_kodu.strip()
            })

        ilave_deger_listesi = []
        for ilave_deger in ereport.rapor_ilave_deger_listesi2:
            ilave_deger_listesi.append({
                'turu': int(ilave_deger.turu) if ilave_deger.turu else '',
                'degeri': ilave_deger.deger.strip() if ilave_deger.deger else '',
                'aciklama': ilave_deger.aciklama.strip() if ilave_deger.aciklama else ''
            })

        vals = {
            'arg0': {
                'tesisKodu': ereport.facility_code.strip(),
                'doktorTcKimlikNo': rapor_olusturan_doktor.doctor_id.strip(),
                'eraporDVO': {
                    'tesisKodu': ereport.facility_code.strip(),
                    'raporTakipNo': ereport.
                    report_follow_no,
                    'hastaTcKimlikNo': patient.tc_no.strip(),
                    'raporNo': ereport.report_no.strip(),
                    'raporTarihi': str(ereport.rapor_tarihi.day) + '.' + str(ereport.rapor_tarihi.month) + '.' + str(
                        ereport.rapor_tarihi.year),
                    'protokolNo': ereport.protokol_no.strip(),
                    'aciklama': '',
                    'klinikTani': '',
                    'raporDuzenlemeTuru': ereport.rapor_duzenleme_turu.strip(),
                    'takipNo': ereport.tracking_no if ereport.facility_code != '11069904' else '',
                    'raporOnayDurumu': ereport.rapor_onay_durumu.strip(),
                    'kisiDVO': {
                        'adi': patient.name.strip(),
                        'cinsiyeti': 'E' if patient.gender == 'male' else 'K' if patient.gender == 'female' else 'other',
                        'dogumTarihi': str(patient.birth.day) + '.' + str(patient.birth.month) + '.' + str(
                            patient.birth.year),
                        'soyadi': patient.surname.strip(),
                        'tcKimlikNo': int(patient.tc_no)
                    },
                    'eraporTeshisListesi': teshis_listesi,
                    'eraporDoktorListesi': doktor_listesi,
                    'eraporEtkinMaddeListesi': etkin_madde_listesi,
                    'eraporAciklamaListesi': aciklama_listesi,
                    'eraporTaniListesi': tani_listesi,
                    'eraporIlaveDegerListesi': ilave_deger_listesi
                }
            }
        }

        with client.settings(strict=False):
            erapor = client.service.eraporGiris(**vals)

        if erapor.sonucKodu == '0000':
            ereport.report_follow_no = erapor.eraporDVO.raporTakipNo
            if ereport.rapor_duzenleme_turu == '2':     # uzman hekim
                ereport.rapor_onay_durumu = '2'
                ereport.state = 'onaylandi'
            else:
                ereport.rapor_onay_durumu = '1'         # heyet
                ereport.state = 'heyet_onayinda'

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
