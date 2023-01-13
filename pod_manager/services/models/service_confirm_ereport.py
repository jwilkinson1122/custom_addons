# -*- coding: utf8 -*-

#
#
# -*- E-Report Onay Servisi -*-
#
#
from lxml import etree

from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class ConfirmEreport(models.Model):
    _name = "podiatry.service.confirm.ereport"
    _description = "Podiatry Confirm E-Report Service"

    doctor_id = fields.Many2one('podiatry.doctor', string="Doctor")
    ereport_id = fields.Integer()

    def confirm_ereport(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiRaporIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        ereport = self.env['podiatry.ereport'].search(
            [('id', '=', self.ereport_id)])

        vals = {
            'arg0': {
                'tesisKodu': int(ereport.facility_code),
                'raporTakipNo': ereport.report_follow_no,
                'doktorTcKimlikNo': self.doctor_id.doctor_id
            }
        }
        with client.settings(strict=False):
            erapor = client.service.eraporOnay(**vals)

        if erapor.sonucKodu == '0000':

            ereport.onaylayan_doktorlar = [(4, self.doctor_id)]

            return {
                'name': 'Sonuç Mesajı',
                'type': 'ir.actions.act_window',
                'res_model': 'sonuc.mesaji.wizard',
                'target': 'new',
                'view_mode': 'form',
                'context': {
                    'default_sonuc_kodu': erapor.sonucKodu,
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
                    'default_sonuc_kodu': erapor.sonucKodu,
                    'default_sonuc_mesaji': erapor.sonucMesaji,
                }
            }
