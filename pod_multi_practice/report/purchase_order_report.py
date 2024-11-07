# -*- coding: utf-8 -*-

from odoo import fields, models


class PurchaseReport(models.Model):
    """inherited purchase report"""

    _inherit = "purchase.report"

    practice_id = fields.Many2one("res.practice", "Practice", readonly=True)

    def _select(self):
        """select"""
        return (
            super(PurchaseReport, self)._select() + ", spt.practice_id as practice_id"
        )

    def _group_by(self):
        """group by"""
        return super(PurchaseReport, self)._group_by() + ", spt.practice_id"
