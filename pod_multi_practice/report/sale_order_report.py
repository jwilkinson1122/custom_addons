# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    practice_id = fields.Many2one("res.practice", readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["practice_id"] = "s.practice_id"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            s.practice_id"""
        return res
