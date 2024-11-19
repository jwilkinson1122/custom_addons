# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date, datetime


class patient_rounding_vaccine(models.Model):
    _name = "patient.rounding.vaccine"
    _description = "pod patient rounding vaccine"

    vaccine_id = fields.Many2one("product.product", string="Vaccines", required=True)
    quantity = fields.Integer(string="Quantity")
    lot_id = fields.Many2one("stock.lot", string="Lot", required=True)
    dose = fields.Integer(string="Dose")
    next_dose_date = fields.Datetime(string="Next Dose")
    short_comment = fields.Char(string="Comment")
    patient_rounding_vaccine_id = fields.Many2one("patient.rounding", string="Vaccine")
