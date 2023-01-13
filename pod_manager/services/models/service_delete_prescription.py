# -*- coding: utf8 -*-

#
#
# -*- Prescriptions Sil Servisi -*-
#
#


from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class DeletePrescription(models.Model):
    _name = "podiatry.service.delete.prescription"
    _description = "Podiatry Delete Prescription Service"

    address_no = fields.Char(string="Prescriptions No")
    facility_code = fields.Char(string="Facility Code")
    doctor_id = fields.Many2one('podiatry.doctor', string="Doctor")

    def delete_prescription(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiReceteIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        vals = {
            'arg0': {
                'tesisKodu': int(self.facility_code),
                'ereceteNo': self.address_no,
                'doktorTcKimlikNo': int(self.doctor_id.doctor_id)
            }
        }

        erecete = client.service.ereceteSil(**vals)

        if erecete.sonucKodu == '0000':
            prescription = self.env['podiatry.prescription'].search(
                [('address_no', '=', self.address_no)])
            prescription.address_no = False
            prescription.state = 'deleted'

        return {
            'name': 'Sonuç Mesajı',
            'type': 'ir.actions.act_window',
            'res_model': 'sonuc.mesaji.wizard',
            'target': 'new',
            'view_mode': 'form',
            'context': {
                'default_sonuc_kodu': erecete.sonucKodu,
                'default_sonuc_mesaji': erecete.sonucMesaji if erecete.sonucKodu != '0000' else 'İşlem Başarılı'
            }
        }
