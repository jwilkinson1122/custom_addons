# -*- coding: utf8 -*-

#
#
# -*- E-Report Liste Sorgula Servisi -*-
#
#
import datetime

from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class QueryEreportList(models.Model):
    _name = "service.query.ereport.list"
    _description = "Hospital Query E-report List Service"

    tesis_kod = fields.Char(string="Facility Code")
    doctor_id = fields.Many2one('hospital.doctor', string="Doctor")
    patient_id = fields.Many2one('hospital.epatient', string="Hasta")
    ereports_list = fields.Many2many(
        'hospital.ereport', string="Hastaya ait e-raporlar")

    def query_ereport_list(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiRaporIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        vals = {
            'arg0': {
                'tesisKodu': int(self.tesis_kod),
                'doktorTcKimlikNo': int(self.doctor_id.doctor_tc),
                'hastaTcKimlikNo': int(self.patient_id.tc_no)
            }
        }

        with client.settings(strict=False):
            erapor = client.service.eraporListeSorgula(**vals)
        result = erapor.eraporListesi

        if erapor.sonucKodu == '0000':

            for rapor in result:

                ereport = self.env['hospital.ereport'].search(
                    [('rapor_no', '=', rapor.raporNo.strip())])
                if ereport:
                    self.ereports_list = [(4, ereport.id)]

            return {
                'name': 'Sorgu Sonucu',
                'type': 'ir.actions.act_window',
                'res_model': 'ereport.list.query.wizard',
                'target': 'new',
                'view_mode': 'form',
                'context': {
                    'default_patient_name': self.patient_id.name,
                    'default_patient_surname': self.patient_id.surname,
                    'default_ereports_list': [(4, erep.id) for erep in self.ereports_list]
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
