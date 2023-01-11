# -*- coding: utf8 -*-
import dateutil.utils

from odoo import models, fields, api


class EReportExplanation(models.Model):

    _name = "hospital.ereport.explanation"
    _description = "Hospital E-Report Explanation"

    ereport_id = fields.Many2one('hospital.ereport')
    service_exp_id = fields.Many2one('hospital.service.add.ereport.explanation')
    aciklama = fields.Text(string="Açıklama")
    takip_formu_no = fields.Char(string="Takip Formu No")
