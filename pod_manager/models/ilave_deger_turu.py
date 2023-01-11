# -*- coding: utf8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class IlaveDegerTuru(models.Model):
    _name = "podiatry.ereport.ilave_deger_turu"

    parametre_adi = fields.Integer(string="Parametre Adı")
    acik_adi = fields.Text(string="Açık Adı")
