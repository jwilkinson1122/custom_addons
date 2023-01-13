# -*- coding: utf8 -*-

#
#
# -*- Kişi Kullanımı Bitmemiş ilaç Sorgulama Servisi -*-
#
#


from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class QueryUnfinishedMedicine(models.Model):
    _name = "podiatry.service.query.unfinished.medicine"
    _description = "Podiatry Query Unfinished Medicine"

    facility_code = fields.Char(string="Facility Code")
    doctor_id = fields.Many2one('podiatry.doctor', string="Doctor")
    patient_id = fields.Many2one('podiatry.patient', string="Hasta")

    def query_unfinished_medicine(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiReceteIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        vals = {
            'arg0': {
                'tesisKodu': self.facility_code,
                'doktorTcKimlikNo': int(self.doctor_id.doctor_tc),
                'hastaTcKimlikNo': int(self.patient_id.tc_no)
            }
        }

        return {
            'name': 'Sonuç Mesajı',
            'type': 'ir.actions.act_window',
            'res_model': 'sonuc.mesaji.wizard',
            'target': 'new',
            'view_mode': 'form',
            'context': {
                'default_sonuc_kodu': client.service.kisiKullanimiBitmemisIlacSorgula(**vals).sonucKodu,
                'default_sonuc_mesaji': client.service.kisiKullanimiBitmemisIlacSorgula(**vals).sonucMesaji,
            }
        }
