# -*- coding: utf8 -*-

#
#
# -*- Prescriptions Sorgula Servisi -*-
#
#
import datetime

from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class QueryPrescription(models.Model):
    _name = "podiatry.service.query.prescription"
    _description = "Podiatry Query Prescription Service"

    address_no = fields.Char(string="Prescriptions No")
    facility_code = fields.Char(string="Facility Code")
    doctor_id = fields.Many2one('podiatry.doctor', string="Doctor")

    def query_prescription(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiReceteIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        prescription = self.env['podiatry.prescription'].search(
            [('address_no', '=', self.address_no.strip())])

        vals = {
            'arg0': {
                'tesisKodu': int(self.facility_code),
                'ereceteNo': self.address_no,
                'doktorTcKimlikNo': int(self.doctor_id.doctor_id)
            }
        }

        erecete = client.service.ereceteSorgula(**vals)
        result = erecete.ereceteDVO

        if erecete.sonucKodu == '0000':
            diagnoises_list = []
            explanations_list = []
            medicines_list = []
            medicine_explanations_list = []
            for diagnosis in result.ereceteTaniListesi:
                diagnoises_list.append({
                    'tani_kodu': diagnosis.taniKodu.strip(),
                    'tani_adi': diagnosis.taniAdi.strip()
                })

            for explanation in result.ereceteAciklamaListesi:
                explanations_list.append({
                    'aciklama_turu': str(explanation.aciklamaTuru),
                    'aciklama': explanation.aciklama
                })

            for medicine in result.ereceteIlacListesi:
                for medicine_explanation in medicine.ereceteIlacAciklamaListesi:
                    medicine_explanations_list.append({
                        'aciklama_turu': str(medicine_explanation.aciklamaTuru),
                        'aciklama': medicine_explanation.aciklama
                    })
                medicines_list.append({
                    'prescription_id': prescription.id,
                    'product_id': self.env['podiatry.ilac'].search([('barcode', '=', medicine.barkod)]).id,
                    'kullanim_sekli': medicine.kullanimSekli,
                    'kullanim_doz1': medicine.kullanimDoz1,
                    'kullanim_doz2': medicine.kullanimDoz2,
                    'kullanim_periyot': medicine.kullanimPeriyot,
                    'kullanim_periyot_birimi': str(medicine.kullanimPeriyotBirimi),
                    'explanation_line_ids': medicine_explanations_list
                })

            return {
                'name': 'Sorgu Sonucu',
                'type': 'ir.actions.act_window',
                'res_model': 'podiatry.prescription.wizard',
                'target': 'new',
                'view_mode': 'form',
                'context': {
                    'default_erecete_no': self.address_no.strip(),
                    'default_today': datetime.datetime.strptime(result.receteTarihi, "%d.%m.%Y"),
                    'default_reference_no': result.seriNo.strip(),
                    'default_protokol_no': result.protokolNo.strip(),
                    'default_takip_no': result.takipNo.strip(),
                    'default_provizyon_tip': str(result.provizyonTipi),
                    'default_tesis_kod': str(result.tesisKodu),
                    'default_recete_tur': str(result.receteTuru),
                    'default_recete_alt_tur': str(result.receteAltTuru),
                    'default_patient_id': self.env['podiatry.patient'].search([('tc_no', '=', str(result.kisiDVO.tcKimlikNo))], limit=1).id,
                    'default_patient_name': result.kisiDVO.adi.strip(),
                    'default_patient_surname': result.kisiDVO.soyadi.strip(),
                    'default_doctor_id': self.env['podiatry.doctor'].search([('doctor_id', '=', str(result.tcKimlikNo))], limit=1).id,
                    'default_practice_id': str(result.doktorBransKodu),
                    'default_state': 'sent',
                    'default_diagnosis_line_ids': [(4, diagnosis.id) for diagnosis in prescription.diagnosis_line_ids] if prescription else diagnoises_list,
                    'default_explanation_line_ids': [(4, explanation.id) for explanation in prescription.explanation_line_ids] if prescription else explanations_list,
                    'default_pharmacy_line_ids': [(4, pharmacy.id) for pharmacy in prescription.pharmacy_line_ids] if prescription else medicines_list
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
                    'default_sonuc_kodu': client.service.ereceteSorgula(**vals).sonucKodu,
                    'default_sonuc_mesaji': client.service.ereceteSorgula(**vals).sonucMesaji,
                }
            }
