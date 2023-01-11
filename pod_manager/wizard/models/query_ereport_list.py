# -*- coding: utf8 -*-
import datetime

from odoo import models, fields, api


class QueryEreportListWizard(models.TransientModel):

    _name = "ereport.list.query.wizard"
    _description = "E-Report Listesi Wizard"

    patient_name = fields.Char(string="Hasta Adı")
    patient_surname = fields.Char(string="Hasta Last Name")
    ereports_list = fields.Many2many(
        'podiatry.ereport', string="Hastaya ait e-raporlar")
