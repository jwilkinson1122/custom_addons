# -*- coding: utf8 -*-

#
#
# -*- E-Report Etkin Madde Ekleme Servisi -*-
#
#
from odoo import models, fields, api
from zeep.wsse.username import UsernameToken
from zeep import Client


class AddEreportExplanation(models.Model):
    _name = "podiatry.service.add.ereport.etkinm"
    _description = "Podiatry Add E-Report Etkin Madde Service"

    ereport_id = fields.Integer()
    doctor_id = fields.Many2one('podiatry.doctor', string="Doctor")
    etkin_madde_lines = fields.Many2many(
        'podiatry.etkin_madde', string="Explanation Lines")

    def add_etkin_madde(self):
        wsdl = "https://sgkt.sgk.gov.tr/medula/eczane/saglikTesisiRaporIslemleriWS?wsdl"
        client = Client(wsdl=wsdl, wsse=UsernameToken(
            '99999999990', '99999999990'))

        ereport = self.env['podiatry.ereport'].search(
            [('id', '=', self.ereport_id)])

        etkin_madde_listesi = []
        for etkin_madde in self.etkin_madde_lines:
            etkin_maddedvo = self.env['podiatry.etkin_maddedvo'].search(
                [('id', '=', etkin_madde.etkin_maddedvo_id.id)])
            etkin_madde_listesi.append({
                'etkinMaddeKodu': etkin_madde.etkin_madde_kodu,
                'kullanimDoz1': etkin_madde.kullanim_doz1,
                'kullanimDoz2': etkin_madde.kullanim_doz2,
                'kullanimDozBirimi': etkin_madde.kullanim_doz_birimi.strip(),
                'kullanimDozPeriyot': etkin_madde.kullanim_doz_periyot,
                'kullanimDozPeriyotBirimi': etkin_madde.kullanim_doz_periyot_birimi.strip(),
                'etkinMaddeDVO': {
                    'kodu': etkin_maddedvo.etkin_madde_kodu.strip(),
                    'adi': etkin_maddedvo.etkin_madde_adi.strip(),
                    'icerikMiktari': str(etkin_maddedvo.etkin_madde_icerik_miktari),
                    'formu': etkin_maddedvo.etkin_madde_formu.strip()
                }
            })

        vals = {
            'arg0': {
                'raporTakipNo': ereport.report_follow_no,
                'tesisKodu': ereport.facility_code,
                'doktorTcKimlikNo': self.doctor_id.doctor_id,
                'eraporEtkinMaddeDVO': etkin_madde_listesi
            }
        }
        erapor = client.service.eraporEtkinMaddeEkle(**vals)

        if erapor.sonucKodu == '0000':
            # model = self._context.get('active_model')
            # active_id = self._context.get('active_id')
            # active_model_id = self.env[model].browse(active_id)
            ereport.rapor_etkin_madde_listesi = [
                (4, new_etkin_madde.id) for new_etkin_madde in self.etkin_madde_lines]

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
