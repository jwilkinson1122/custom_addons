# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date, datetime


class patient_pregnency(models.Model):
    _name = "patient.pregnency"
    _description = "medical patient pregnency"

    gravida = fields.Integer("Pregnancy #")
    lmp = fields.Integer("LMP")
    pdd = fields.Date("Pregnency  Due Date")
    patient_id = fields.Many2one("patient", "Patient")
    current_pregnency = fields.Boolean("Current Pregnency")
    patient_evolution_prental_ids = fields.One2many(
        "patient.prental.evoultion",
        "pregnency_id",
        "Patient Perinatal Evaluations",
    )
    perinatal_ids = fields.One2many("preinatal", "pregnency_id", "Perinatal ")
    puerperium_perental_ids = fields.One2many(
        "puerperium.monitor", "pregnency_id", "Puerperium Monitor"
    )
    fetuses = fields.Boolean("Fetuses")
    monozygotic = fields.Boolean("Monozygotic")
    igur = fields.Selection([("s", "Symmetric"), ("a", "Asymmetric")], "IGUR")
    warn = fields.Boolean("Warning")
    result = fields.Char("Result")
    pregnancy_end_date = fields.Date("Pregnancy End Date")
    pregnancy_end_result = fields.Char("Pregnancy End Result")


# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
