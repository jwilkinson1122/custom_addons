# -*- coding: utf-8 -*-


from odoo import fields, models


class PrescriptionReport(models.Model):
    _inherit = "prescriptions.report"

    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['warehouse_id'] = "s.warehouse_id"
        return res

    def _group_by_prescription(self):
        res = super()._group_by_prescription()
        res += """,
            s.warehouse_id"""
        return res
