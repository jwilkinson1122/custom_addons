# -*- coding: utf8 -*-
import dateutil.utils

from odoo import models, fields, api


class EtkinMaddeDVO(models.Model):

    _name = "podiatry.etkin_maddedvo"
    _description = "Podiatry Etkin Madde DVO"
    _rec_name = 'etkin_madde_kodu'

    etkin_madde_kodu = fields.Char(string="Active Item Code")
    etkin_madde_adi = fields.Char(string="Etkin Madde Adı")
    etkin_madde_icerik_miktari = fields.Float(string="İçerik Miktarı")
    etkin_madde_formu = fields.Char(string="Formu")
