# -*- coding: utf8 -*-
import dateutil.utils

from odoo import models, fields, api


class Condition(models.Model):

    _name = "hospital.diagnosis"
    _description = "Hospital Condition"
    _rec_name = 'tani_kodu'

    tani_kodu = fields.Char(string="Tanı Kodu")
    tani_adi = fields.Char(string="Tanı Adı")
