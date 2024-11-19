# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class patient_rounding_supply(models.Model):
    _name = "patient.rounding.supply"
    _description = "pod patient rounding pod supply"

    product_id = fields.Many2one(
        "product.product", string="Podiatry Supply", required=True
    )
    short_comment = fields.Char(string="Comment")
    quantity = fields.Integer(string="Quantity")
    lot_id = fields.Many2one("stock.lot", string="Lot", required=True)
    patient_rounding_supply_id = fields.Many2one(
        "patient.rounding", string=" Podiatry Supplies "
    )
