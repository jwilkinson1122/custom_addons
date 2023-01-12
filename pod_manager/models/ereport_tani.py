# -*- coding: utf8 -*-
import dateutil.utils

from odoo import models, fields, api


class EReportTani(models.Model):

    _name = "podiatry.ereport.tani"
    _description = "Podiatry E-Report Tanı"
    _rec_name = 'tani_kodu'

    tani_kodu = fields.Char(string="Tanı Kodu")
    tani_adi = fields.Char(string="Tanı Adı")
