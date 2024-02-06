# -*- coding: utf-8 -*-


from odoo import fields, models

# class OrderReport(models.AbstractModel):
#     _name = "prescription.report_prescription_order"
#     _description = "Auxiliar to get the report"

 
class PrescriptionReport(models.AbstractModel):
    _inherit = "prescription.report_prescription_order"

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
