# -*- coding: utf8 -*-

#
#
# -*- Açıklama Ekleme Servisi -*-
#
#


from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class AddExplanation(models.Model):
    _name = "podiatry.service.add.explanation"
    _description = "Podiatry Add explanation Service"

    prescription_id = fields.Integer()
    doctor_id = fields.Many2one('podiatry.doctor', string="Doctor")
    explanation_lines = fields.One2many('prescription.explanation.lines', 'service_exp_id',
                                        string="Explanation Lines")

    def add_explanation(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiReceteIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        prescription = self.env['podiatry.prescription'].search(
            [('id', '=', self.prescription_id)])

        explanation_list = []
        for new_exp in self.explanation_lines:
            explanation_list.append({
                'aciklamaTuru': int(new_exp.aciklama_turu),
                'aciklama': new_exp.aciklama
            })

        vals = {
            'arg0': {
                'ereceteNo': prescription.address_no,
                'tesisKodu': int(prescription.facility_code),
                'doktorTcKimlikNo': int(self.doctor_id.doctor_id),
                'ereceteAciklamaDVO': explanation_list
            }
        }
        erecete = client.service.ereceteAciklamaEkle(**vals)

        if erecete.sonucKodu == '0000':
            # model = self._context.get('active_model')
            # active_id = self._context.get('active_id')
            # active_model_id = self.env[model].browse(active_id)
            prescription.explanation_line_ids = [
                (4, explanation.id) for explanation in self.explanation_lines]
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


# Prescriptions Add Description
class PrescriptionsServiceExplanationLines(models.Model):
    _name = "prescription.service.explanation.lines"
    _description = "Prescription Explanation Lines"

    service_exp_id = fields.Many2one('podiatry.service.add.explanation')
    aciklama_turu = fields.Selection([
        ('1', 'Teşhis/Tanı'),
        ('2', 'Tedavi Süresi'),
        ('3', 'Hasta Güvenlik ve İzleme Formu'),
        ('4', 'Tetkik Sonucu'),
        ('5', 'Endikasyon Dışı Kullanım İzni'),
        ('99', 'Other')
    ], string="Açıklama Type")
    aciklama = fields.Text(string="Prescriptions Açıklaması")
