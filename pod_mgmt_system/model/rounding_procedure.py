# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class rounding_procedure(models.Model):
    _name = "rounding_procedure"
    _description = "pod rounding procedure"

    notes = fields.Text(string="Notes")
    patient_rounding_procedure_id = fields.Many2one(
        "patient.rounding", string="Vaccines"
    )
