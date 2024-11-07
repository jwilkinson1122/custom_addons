# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockWarehouse(models.Model):
    """inherited stock warehouse"""

    _inherit = "stock.warehouse"

    @api.model
    def _get_default_practice(self):
        """method to get default practice"""
        practice_id = self.env.user.practice_id
        return practice_id

    def _get_practice_domain(self):
        """method to get practice domain"""
        company = self.env.company
        practice_ids = self.env.user.practice_ids
        practice = practice_ids.filtered(
            lambda practice: practice.company_id == company
        )
        return [("id", "in", practice.ids)]

    practice_id = fields.Many2one(
        "res.practice",
        string="Practice",
        store=True,
        default=_get_default_practice,
        domain=_get_practice_domain,
        help="Leave this field empty if this warehouse "
        " is shared between all practices",
    )


class PracticeStockMove(models.Model):
    """inherited stock.move"""

    _inherit = "stock.move"

    practice_id = fields.Many2one(
        "res.practice", readonly=True, store=True, related="picking_id.practice_id"
    )


class PracticeStockMoveLine(models.Model):
    """inherited stock move line"""

    _inherit = "stock.move.line"

    practice_id = fields.Many2one(
        "res.practice", readonly=True, store=True, related="move_id.practice_id"
    )


class PracticeStockValuationLayer(models.Model):
    """Inherited Stock Valuation Layer"""

    _inherit = "stock.valuation.layer"

    practice_id = fields.Many2one(
        "res.practice", readonly=True, store=True, related="stock_move_id.practice_id"
    )
