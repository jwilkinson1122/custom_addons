# -*- coding: utf8 -*-
import dateutil.utils

from odoo import models, fields, api


class Teshis(models.Model):
    _name = "podiatry.ereport.teshis"
    _description = "Hospital Teshis"
    _rec_name = 'rapor_teshis_kodu'

    rapor_teshis_kodu = fields.Char(string="Diagnostic Code")
    rapor_teshis_adi = fields.Text(string="Teşhis Adı")

    def name_get(self):
        result = []
        for rec in self:
            name = rec.rapor_teshis_kodu + ' : ' + rec.rapor_teshis_adi
            result.append((rec.id, name))
        return result
