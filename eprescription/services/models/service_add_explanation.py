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
    _name = "hospital.service.add.explanation"
    _description = "Hospital Add explanation Service"

    eprescription_id = fields.Integer()
    doctor_id = fields.Many2one('hospital.doctor', string="Doctor")
    explanation_lines = fields.One2many('eprescription.explanation.lines', 'service_exp_id',
                                        string="Explanation Lines")

    def add_explanation(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiReceteIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        eprescription = self.env['hospital.eprescription'].search(
            [('id', '=', self.eprescription_id)])

        explanation_list = []
        for new_exp in self.explanation_lines:
            explanation_list.append({
                'aciklamaTuru': int(new_exp.aciklama_turu),
                'aciklama': new_exp.aciklama
            })

        vals = {
            'arg0': {
                'ereceteNo': eprescription.erecete_no,
                'tesisKodu': int(eprescription.tesis_kod),
                'doktorTcKimlikNo': int(self.doctor_id.doctor_tc),
                'ereceteAciklamaDVO': explanation_list
            }
        }
        erecete = client.service.ereceteAciklamaEkle(**vals)

        if erecete.sonucKodu == '0000':
            # model = self._context.get('active_model')
            # active_id = self._context.get('active_id')
            # active_model_id = self.env[model].browse(active_id)
            eprescription.explanation_line_ids = [
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


# E-Prescriptions Add Description
class EprescriptionsServiceExplanationLines(models.Model):
    _name = "eprescription.service.explanation.lines"
    _description = "E-Prescription Explanation Lines"

    service_exp_id = fields.Many2one('hospital.service.add.explanation')
    aciklama_turu = fields.Selection([
        ('1', 'Teşhis/Tanı'),
        ('2', 'Tedavi Süresi'),
        ('3', 'Hasta Güvenlik ve İzleme Formu'),
        ('4', 'Tetkik Sonucu'),
        ('5', 'Endikasyon Dışı Kullanım İzni'),
        ('99', 'Other')
    ], string="Açıklama Type")
    aciklama = fields.Text(string="E-Prescriptions Açıklaması")
