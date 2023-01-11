# -*- coding: utf8 -*-
import datetime

from odoo import models, fields, api


class QueryPrescriptionListWizard(models.TransientModel):

    _name = "prescription.list.query.wizard"
    _description = "Prescriptions Listesi Wizard"

    patient_name = fields.Char(string="Hasta Adı")
    patient_surname = fields.Char(string="Hasta Last Name")
    prescriptions_list = fields.Many2many(
        'podiatry.prescription', string="Hastaya ait e-reçeteler")
