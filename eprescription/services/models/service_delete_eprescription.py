# -*- coding: utf8 -*-

#
#
# -*- E-Prescriptions Sil Servisi -*-
#
#


from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class DeleteEprescription(models.Model):
    _name = "hospital.service.delete.eprescription"
    _description = "Hospital Delete Eprescription Service"

    erecete_no = fields.Char(string="E-Prescriptions No")
    tesis_kod = fields.Char(string="Facility Code")
    doctor_id = fields.Many2one('hospital.doctor', string="Doctor")

    def delete_eprescription(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiReceteIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        vals = {
            'arg0': {
                'tesisKodu': int(self.tesis_kod),
                'ereceteNo': self.erecete_no,
                'doktorTcKimlikNo': int(self.doctor_id.doctor_tc)
            }
        }

        erecete = client.service.ereceteSil(**vals)

        if erecete.sonucKodu == '0000':
            eprescription = self.env['hospital.eprescription'].search(
                [('erecete_no', '=', self.erecete_no)])
            eprescription.erecete_no = False
            eprescription.state = 'deleted'

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
