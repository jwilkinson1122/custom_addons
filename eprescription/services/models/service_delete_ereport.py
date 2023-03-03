# -*- coding: utf8 -*-

#
#
# -*- E-Report Sil Servisi -*-
#
#


from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class DeleteEreport(models.Model):
    _name = "hospital.service.delete.ereport"
    _description = "Hospital Delete E-Report Service"

    rapor_takip_no = fields.Char(string="ReportFollow up No")
    tesis_kod = fields.Char(string="Facility Code")
    doctor_id = fields.Many2one('hospital.doctor', string="Doctor")

    def delete_ereport(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiRaporIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        ereport = self.env['hospital.ereport'].search(
            [('rapor_takip_no', '=', self.rapor_takip_no)])

        vals = {
            'arg0': {
                'tesisKodu': int(self.tesis_kod),
                'raporTakipNo': self.rapor_takip_no,
                'doktorTcKimlikNo': self.doctor_id.doctor_tc
            }
        }

        erapor = client.service.eraporSil(**vals)

        if erapor.sonucKodu == '0000':

            ereport.rapor_takip_no = False
            ereport.state = 'deleted'

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
