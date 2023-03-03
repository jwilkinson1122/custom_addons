# -*- coding: utf8 -*-

#
#
# -*- E-Report Teşhise Tanı Ekleme Servisi -*-
#
#
from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class AddEreportTeshisTani(models.Model):
    _name = "hospital.service.add.ereport.teshist"

    teshis_id = fields.Integer()
    doctor_id = fields.Many2one('hospital.doctor', string="Doctor")
    tani_lines = fields.Many2many(
        'hospital.diagnosis', string="Condition List")

    def add_teshis_tani(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiRaporIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        teshis = self.env['ereport.teshis.line'].search(
            [('id', '=', self.env.context['active_id'])])
        ereport_id = teshis.ereport_id
        ereport = self.env['hospital.ereport'].search(
            [('id', '=', ereport_id)])

        tani_list = []
        for new_tani in self.tani_lines:
            tani_list.append({
                'taniAdi': new_tani.tani_adi,
                'taniKodu': new_tani.tani_kodu
            })

        vals = {
            'arg0': {
                'raporTakipNo': ereport.rapor_takip_no,
                'tesisKodu': ereport.tesis_kod,
                'doktorTcKimlikNo': self.doctor_id.doctor_tc,
                'raporTeshisKodu': str(teshis.rapor_teshis_kodu.rapor_teshis_kodu),
                'eraporTaniDVO': tani_list
            }
        }
        erapor = client.service.eraporTaniEkle(**vals)

        if erapor.sonucKodu == '0000':
            # model = self._context.get('active_model')
            # active_id = self._context.get('active_id')
            # active_model_id = self.env[model].browse(active_id)
            teshis.tani_listesi = [(4, tani.id) for tani in self.tani_lines]

        return {
            'name': 'Sonuç Mesajı',
            'type': 'ir.actions.act_window',
            'res_model': 'sonuc.mesaji.wizard',
            'target': 'new',
            'view_mode': 'form',
            'context': {
                'default_sonuc_kodu': erapor.sonucKodu,
                'default_sonuc_mesaji': erapor.sonucMesaji if erapor.sonucKodu != '0000' else 'İşlem Başarılı!',
            }
        }
