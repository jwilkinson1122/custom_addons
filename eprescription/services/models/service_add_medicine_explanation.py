# -*- coding: utf8 -*-

#
#
# -*- İlaç Açıklama Ekleme Servisi -*-
#
#


from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class AddMedicineExplanation(models.Model):
    _name = "hospital.service.add.medicine.explanation"
    _description = "Hospital Add Medicine Explanation Service"

    pharmacy_line_id = fields.Integer()
    doctor_id = fields.Many2one('hospital.doctor', string="Doctor")
    medicine_explanation_lines = fields.One2many('eprescription.medicine.explanation.lines', 'service_medicine_exp_id',
                                                 string="İlaç Description List")

    def add_medicine_explanation(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiReceteIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        pharmacy_line = self.env['eprescription.pharmacy.lines2'].search(
            [('id', '=', self.pharmacy_line_id)])
        eprescription = self.env['hospital.eprescription'].search(
            [('id', '=', pharmacy_line.eprescription_id.id)])

        medicine_explanation_list = []
        for explanation in self.medicine_explanation_lines:
            medicine_explanation_list.append({
                'aciklamaTuru': int(explanation.aciklama_turu),
                'aciklama': explanation.aciklama
            })

        vals = {
            'arg0': {
                'ereceteNo': eprescription.erecete_no,
                'barkod': int(pharmacy_line.product_id.barcode),
                'tesisKodu': int(eprescription.tesis_kod),
                'doktorTcKimlikNo': int(self.doctor_id.doctor_tc),
                'ereceteIlacAciklamaDVO': medicine_explanation_list
            }
        }

        erecete = client.service.ereceteIlacAciklamaEkle(**vals)

        if erecete.sonucKodu == '0000':
            pharmacy_line.explanation_line_ids = [
                (4, explanation.id) for explanation in self.medicine_explanation_lines]
            return {
                'name': 'Sonuç Mesajı',
                'type': 'ir.actions.act_window',
                'res_model': 'sonuc.mesaji.wizard',
                'target': 'new',
                'view_mode': 'form',
                'context': {
                    'default_sonuc_kodu': erecete.sonucKodu,
                    'default_sonuc_mesaji': 'İşlem Başarılı!',
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
                    'default_sonuc_kodu': erecete.sonucKodu,
                    'default_sonuc_mesaji': erecete.sonucMesaji,
                }
            }
