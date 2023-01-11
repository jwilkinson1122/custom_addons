# -*- coding: utf8 -*-

#
#
# -*- Prescriptions Giriş Servisi -*-
#
#


from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class SavePrescription(models.Model):
    _name = "podiatry.service.save.prescription"
    _description = "Hospital Prescriptions Save Service"

    prescription_id = fields.Integer()

    def save_prescription(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiReceteIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        pharmacy_line_vals_erecete_ilac_listesi = []
        pharmacy_line_vals_erecete_aciklama_listesi = []
        pharmacy_line_vals_erecete_tani_listesi = []
        pharmacy_line_vals_erecete_ilac_aciklama_listesi = []

        prescription = self.env['podiatry.prescription'].search(
            [('id', '=', self.prescription_id)])

        for i in prescription.pharmacy_line_ids:

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

        for j in prescription.explanation_line_ids:
            pharmacy_line_vals_erecete_aciklama_listesi.append({
                'aciklamaTuru': int(j.aciklama_turu),
                'aciklama': j.aciklama
            })

        for k in prescription.diagnosis_line_ids:
            pharmacy_line_vals_erecete_tani_listesi.append({
                'taniAdi': k.tani_adi if k.tani_adi else '',
                'taniKodu': k.tani_kodu if k.tani_kodu else ''
            })

        vals = {
            'arg0': {
                'ereceteDVO': {
                    'ereceteNo': '',
                    'tesisKodu': int(prescription.facility_code),
                    'tcKimlikNo': int(prescription.patient_id.tc_no),
                    'takipNo': prescription.tracking_no if prescription.facility_code == '11068891' else '',
                    'provizyonTipi': prescription.provizyon_tip,
                    'receteTarihi': str(prescription.today.day) + '.' + str(prescription.today.month) + '.' + str(prescription.today.year),
                    'receteTuru': int(prescription.recete_tur),
                    'receteAltTuru': int(prescription.recete_alt_tur),
                    'protokolNo': prescription.protokol_no,
                    'seriNo': prescription.reference_no,
                    'doktorTcKimlikNo': int(prescription.doctor_id.doctor_tc),
                    'doktorBransKodu': int(prescription.doctor_id.brans_kod),
                    'doktorSertifikaKodu': int(prescription.doctor_id.sertifika_kod),
                    'doktorAdi': prescription.doctor_id.name,
                    'doktorSoyadi': prescription.doctor_id.surname,
                    'kisiDVO': {
                        'tcKimlikNo': int(prescription.patient_id.tc_no),
                        'adi': prescription.patient_id.name,
                        'soyadi': prescription.patient_id.surname,
                        'dogumTarihi': str(prescription.patient_id.birth.day) + '.' + str(
                            prescription.patient_id.birth.month) + '.' + str(prescription.patient_id.birth.year),
                        'cinsiyeti': 'E' if prescription.patient_id.gender == 'male' else 'K'
                    },
                    'ereceteAciklamaListesi': pharmacy_line_vals_erecete_aciklama_listesi,
                    'ereceteTaniListesi': pharmacy_line_vals_erecete_tani_listesi,
                    'ereceteIlacListesi': pharmacy_line_vals_erecete_ilac_listesi
                },
                'tesisKodu': int(prescription.facility_code),
                'doktorTcKimlikNo': int(prescription.doctor_id.doctor_tc),
            }
        }

        erecete = client.service.ereceteGiris(**vals)

        if erecete.sonucKodu == '0000':
            getPrescription = self.env['podiatry.prescription'].search(
                [('reference_no', '=', prescription.reference_no)])
            getprescription.address_no = erecete.ereceteDVO.ereceteNo
            getprescription.state = 'sent'

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
