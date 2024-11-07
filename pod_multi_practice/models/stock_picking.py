# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    """inherited stock.picking"""

    _inherit = "stock.picking"

    def _get_default_practice_id(self):
        if len(self.env.user.practice_ids) == 1:
            sp_company = self.company_id if self.company_id else self.env.company
            practice_ids = self.env.user.practice_ids
            practice = practice_ids.filtered(
                lambda practice: practice.company_id == sp_company
            )
            if practice:
                return practice
            else:
                return False
        return False

    practice_id = fields.Many2one(
        "res.practice",
        string="Practice",
        readonly=False,
        store=True,
        compute="_compute_practice_id",
        default=_get_default_practice_id,
    )

    @api.depends("sale_id", "purchase_id")
    def _compute_practice_id(self):
        """method to compute practice"""
        for record in self:
            record.practice_id = False
            if record.sale_id.practice_id:
                record.practice_id = record.sale_id.practice_id
            if record.purchase_id.practice_id:
                record.practice_id = record.purchase_id.practice_id


class StockPickingTypes(models.Model):
    """inherited stock picking type"""

    _inherit = "stock.picking.type"

    practice_id = fields.Many2one(
        "res.practice",
        string="Practice",
        store=True,
        related="warehouse_id.practice_id",
    )
