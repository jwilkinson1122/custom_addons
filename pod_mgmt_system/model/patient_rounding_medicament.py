# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class patient_rounding_medicament(models.Model):
    _name = "patient.rounding.medicament"
    _description = "pod patient rounding medicament"

    medicament_id = fields.Many2one("medicament", string="Medicament", required=True)
    quantity = fields.Integer(string="Quantity")
    lot_id = fields.Many2one("stock.lot", string="Lot", required=True)
    short_comment = fields.Char(string="Comment")
    product_id = fields.Many2one("product.product", string="Product")
    patient_rounding_medicament_id = fields.Many2one(
        "patient.rounding", string="Medicaments"
    )
