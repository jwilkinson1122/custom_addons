# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date, datetime


class vaccination(models.Model):
    _name = "vaccination"
    _description = "pod vaccination"

    vaccine_product_id = fields.Many2one(
        "product.product", string="Name", required=True
    )
    institution_partner_id = fields.Many2one(
        "res.partner",
        domain=[("is_institution", "=", True)],
        string="Institution",
        required=True,
    )
    next_dose_date = fields.Datetime(string="Next Dose")
    vaccine_expiration_date = fields.Datetime(string="Expiration Date", required=True)
    observations = fields.Char(string="Observations")
    dose = fields.Integer(string="Dose Number", required=True)
    date = fields.Datetime(string="Date", required=True)
    vaccine_lot = fields.Char(string="Lot Number")
    patient_vaccines_id = fields.Many2one("patient", string="Vaccination")
