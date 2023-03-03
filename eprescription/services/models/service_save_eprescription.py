# -*- coding: utf8 -*-

#
#
# -*- E-Prescriptions Giriş Servisi -*-
#
#


from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class SaveEprescription(models.Model):
    _name = "hospital.service.save.eprescription"
    _description = "Hospital E-Prescriptions Save Service"

    eprescription_id = fields.Integer()

    def save_eprescription(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiReceteIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        pharmacy_line_vals_erecete_ilac_listesi = []
        pharmacy_line_vals_erecete_aciklama_listesi = []
        pharmacy_line_vals_erecete_tani_listesi = []
        pharmacy_line_vals_erecete_ilac_aciklama_listesi = []

        eprescription = self.env['hospital.eprescription'].search(
            [('id', '=', self.eprescription_id)])

        for i in eprescription.pharmacy_line_ids:

            for z in i.explanation_line_ids:
                pharmacy_line_vals_erecete_ilac_aciklama_listesi.append({
                    'aciklamaTuru': int(z.aciklama_turu),
                    'aciklama': z.aciklama
                })

            pharmacy_line_vals_erecete_ilac_listesi.append({
                'barkod': int(i.product_id.barcode),
                'adet': i.quantity,
                'ilacAdi': i.medicine_name,
                'kullanimSekli': i.kullanim_sekli,
                'kullanimDoz1': i.kullanim_doz1,
                'kullanimDoz2': i.kullanim_doz2,
                'kullanimPeriyot': i.kullanim_periyot,
                'kullanimPeriyotBirimi': int(i.kullanim_periyot_birimi),
                'geriOdemeKapsaminda': '',
                'ereceteIlacAciklamaListesi': pharmacy_line_vals_erecete_ilac_aciklama_listesi
            })

        for j in eprescription.explanation_line_ids:
            pharmacy_line_vals_erecete_aciklama_listesi.append({
                'aciklamaTuru': int(j.aciklama_turu),
                'aciklama': j.aciklama
            })

        for k in eprescription.diagnosis_line_ids:
            pharmacy_line_vals_erecete_tani_listesi.append({
                'taniAdi': k.tani_adi if k.tani_adi else '',
                'taniKodu': k.tani_kodu if k.tani_kodu else ''
            })

        vals = {
            'arg0': {
                'ereceteDVO': {
                    'ereceteNo': '',
                    'tesisKodu': int(eprescription.tesis_kod),
                    'tcKimlikNo': int(eprescription.patient_id.tc_no),
                    'takipNo': eprescription.takip_no if eprescription.tesis_kod == '11068891' else '',
                    'provizyonTipi': eprescription.provizyon_tip,
                    'receteTarihi': str(eprescription.today.day) + '.' + str(eprescription.today.month) + '.' + str(eprescription.today.year),
                    'receteTuru': int(eprescription.recete_tur),
                    'receteAltTuru': int(eprescription.recete_alt_tur),
                    'protokolNo': eprescription.protokol_no,
                    'seriNo': eprescription.seri_no,
                    'doktorTcKimlikNo': int(eprescription.doctor_id.doctor_tc),
                    'doktorBransKodu': int(eprescription.doctor_id.brans_kod),
                    'doktorSertifikaKodu': int(eprescription.doctor_id.sertifika_kod),
                    'doktorAdi': eprescription.doctor_id.name,
                    'doktorSoyadi': eprescription.doctor_id.surname,
                    'kisiDVO': {
                        'tcKimlikNo': int(eprescription.patient_id.tc_no),
                        'adi': eprescription.patient_id.name,
                        'soyadi': eprescription.patient_id.surname,
                        'dogumTarihi': str(eprescription.patient_id.birth.day) + '.' + str(
                            eprescription.patient_id.birth.month) + '.' + str(eprescription.patient_id.birth.year),
                        'cinsiyeti': 'E' if eprescription.patient_id.gender == 'male' else 'K'
                    },
                    'ereceteAciklamaListesi': pharmacy_line_vals_erecete_aciklama_listesi,
                    'ereceteTaniListesi': pharmacy_line_vals_erecete_tani_listesi,
                    'ereceteIlacListesi': pharmacy_line_vals_erecete_ilac_listesi
                },
                'tesisKodu': int(eprescription.tesis_kod),
                'doktorTcKimlikNo': int(eprescription.doctor_id.doctor_tc),
            }
        }

        erecete = client.service.ereceteGiris(**vals)

        if erecete.sonucKodu == '0000':
            getEprescription = self.env['hospital.eprescription'].search(
                [('seri_no', '=', eprescription.seri_no)])
            getEprescription.erecete_no = erecete.ereceteDVO.ereceteNo
            getEprescription.state = 'sent'

        return {
            'name': 'Sonuç Mesajı',
            'type': 'ir.actions.act_window',
            'res_model': 'sonuc.mesaji.wizard',
            'target': 'new',
            'view_mode': 'form',
            'context': {
                'default_sonuc_kodu': erecete.sonucKodu,
                'default_sonuc_mesaji': erecete.sonucMesaji if erecete.sonucKodu != '0000' else 'İşlem Başarılı!',
            }
        }
