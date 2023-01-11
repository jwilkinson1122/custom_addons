# -*- coding: utf8 -*-

#
#
# -*- E-Report Açıklama Ekleme Servisi -*-
#
#
from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class AddEreportExplanation(models.Model):
    _name = "podiatry.service.add.ereport.explanation"
    _description = "Hospital Add E-Report explanation Service"

    ereport_id = fields.Integer()
    doctor_id = fields.Many2one('podiatry.doctor', string="Doctor")
    explanation_lines = fields.One2many('podiatry.ereport.explanation', 'service_exp_id',
                                        string="Explanation Lines")

    def add_explanation(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiRaporIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        ereport = self.env['podiatry.ereport'].search(
            [('id', '=', self.ereport_id)])

        explanation_list = []
        for new_exp in self.explanation_lines:
            explanation_list.append({
                'takipFormuNo': new_exp.takip_formu_no,
                'aciklama': new_exp.aciklama
            })

        vals = {
            'arg0': {
                'raporTakipNo': ereport.report_follow_no,
                'tesisKodu': ereport.facility_code,
                'doktorTcKimlikNo': self.doctor_id.doctor_tc,
                'eraporAciklamaDVO': explanation_list
            }
        }
        erapor = client.service.eraporAciklamaEkle(**vals)

        if erapor.sonucKodu == '0000':
            # model = self._context.get('active_model')
            # active_id = self._context.get('active_id')
            # active_model_id = self.env[model].browse(active_id)
            ereport.rapor_aciklama_listesi = [
                (4, explanation.id) for explanation in self.explanation_lines]

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
