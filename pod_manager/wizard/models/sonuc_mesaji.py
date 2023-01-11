# -*- coding: utf8 -*-
import datetime

from odoo import models, fields, api


class SonucMesajiWizard(models.TransientModel):

    _name = "sonuc.mesaji.wizard"
    _description = "Sonuç Mesajı Wizard"

    sonuc_kodu = fields.Char(string="Sonuç Kodu", readonly=True)
    sonuc_mesaji = fields.Text(string="Sonuç Mesajı", readonly=True)
