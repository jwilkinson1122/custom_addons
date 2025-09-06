# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    def _get_report_values(self, docids, data=None):
        docs = self.env["sale.order"].browse(docids)
        grouped_lines = {
            "left": [],
            "right": [],
            "bilateral": [],
        }
        for order in docs:
            for line in order.order_line:
                grouped_lines[line.laterality].append(line)

        return {
            "docs": docs,
            "grouped_lines": grouped_lines,
        }

# class SaleReport(models.Model):
#     _inherit = "sale.report"

#     warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', readonly=True)

#     def _select_additional_fields(self):
#         res = super()._select_additional_fields()
#         res['warehouse_id'] = "s.warehouse_id"
#         return res

#     def _group_by_sale(self):
#         res = super()._group_by_sale()
#         res += """,
#             s.warehouse_id"""
#         return res
