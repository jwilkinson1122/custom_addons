# -*- coding: utf8 -*-

#
#
# -*- Prescriptions Liste Sorgula Servisi -*-
#
#
import datetime

from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class QueryPrescriptionList(models.Model):
    _name = "service.query.prescription.list"
    _description = "Hospital Query Prescription List Service"

    facility_code = fields.Char(string="Facility Code")
    doctor_id = fields.Many2one('podiatry.doctor', string="Doctor")
    patient_id = fields.Many2one('podiatry.epatient', string="Hasta")
    prescriptions_list = fields.Many2many(
        'podiatry.prescription', string="Hastaya ait e-reçeteler")

    def query_prescription_list(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiReceteIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        vals = {
            'arg0': {
                'tesisKodu': int(self.facility_code),
                'doktorTcKimlikNo': int(self.doctor_id.doctor_tc),
                'hastaTcKimlikNo': int(self.patient_id.tc_no)
            }
        }

        with client.settings(strict=False):
            erecete = client.service.ereceteListeSorgu(**vals)
        result = erecete.ereceteListesi

        if erecete.sonucKodu == '0000':

            prescription_list = []
            for recete in result:

                prescription = self.env['podiatry.prescription'].search(
                    [('address_no', '=', recete.ereceteNo)])
                if prescription:
                    self.prescriptions_list = [(4, prescription.id)]
                """
                prescriptions_list.append({
                    'reference_no': recete.ereceteNo,
                    'doctor_name': recete.doktorAdi,
                    'doctor_surname': recete.doktorSoyadi,
                    'today': datetime.datetime.strptime(recete.receteTarihi, "%d.%m.%Y")
                })
                """

            return {
                'name': 'Sorgu Sonucu',
                'type': 'ir.actions.act_window',
                'res_model': 'prescription.list.query.wizard',
                'target': 'new',
                'view_mode': 'form',
                'context': {
                    'default_patient_name': self.patient_id.name,
                    'default_patient_surname': self.patient_id.surname,
                    'default_prescriptions_list': [(4, epre.id) for epre in self.prescriptions_list]
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
