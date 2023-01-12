# -*- coding: utf8 -*-
import dateutil.utils

from odoo import models, fields, api


class Explanation(models.Model):

    _name = "podiatry.explanation"
    _description = "Podiatry Explanation"
    _rec_name = 'id'

    aciklama_turu = fields.Selection([
        ('1', 'Teşhis/Tanı'),
        ('2', 'Tedavi Süresi'),
        ('3', 'Hasta Güvenlik ve İzleme Formu'),
        ('4', 'Tetkik Sonucu'),
        ('5', 'Endikasyon Dışı Kullanım İzni'),
        ('99', 'Other')
    ], string="Açıklama Type")
    aciklama = fields.Text(string="Açıklama")
