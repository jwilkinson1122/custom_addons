# -*- coding: utf8 -*-

#
#
# -*- ICD-10 Conditions Adding Service -*-
#
#


from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class AddDiagnosis(models.Model):
    _name = "podiatry.service.add.diagnosis"
    _description = "Hospital Add Condition Service"

    prescription_id = fields.Integer()
    add_diagnoises = fields.Many2many('podiatry.diagnosis', string="Tanılar")
    doctor_id = fields.Many2one('podiatry.doctor', string="Doctor")

    def add_diagnosis(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiReceteIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        prescription = self.env['podiatry.prescription'].search(
            [('id', '=', self.prescription_id)])

        diagnoises_list = []
        for diagnosis in self.add_diagnoises:
            diagnoises_list.append({
                'taniAdi': diagnosis.tani_adi,
                'taniKodu': diagnosis.tani_kodu
            })

        vals = {
            'arg0': {
                'ereceteNo': prescription.address_no,
                'tesisKodu': int(prescription.facility_code),
                'doktorTcKimlikNo': int(self.doctor_id.doctor_tc),
                'ereceteTaniDVO': diagnoises_list
            }
        }

        erecete_tani_ekle = client.service.ereceteTaniEkle(**vals)

        if erecete_tani_ekle.sonucKodu == '0000':
            model = self._context.get('active_model')
            active_id = self._context.get('active_id')
            active_model_id = self.env[model].browse(active_id)
            active_model_id.diagnosis_line_ids = [
                (4, diagnosis.id) for diagnosis in self.add_diagnoises]

        return {
            'name': 'Sonuç Mesajı',
            'type': 'ir.actions.act_window',
            'res_model': 'sonuc.mesaji.wizard',
            'target': 'new',
            'view_mode': 'form',
            'context': {
                'default_sonuc_kodu': erecete_tani_ekle.sonucKodu,
                'default_sonuc_mesaji': erecete_tani_ekle.sonucMesaji if erecete_tani_ekle.sonucKodu != '0000' else 'İşlem Başarılı!',
            }
        }
