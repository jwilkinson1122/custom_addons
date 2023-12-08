# -*- coding: utf-8 -*-


from odoo import api, fields, models


class StockRulesReport(models.TransientModel):
    _inherit = 'stock.rules.report'

    so_route_ids = fields.Many2many('stock.route', string='Apply specific routes',
        domain="[('prescriptions_selectable', '=', True)]", help="Choose to apply RX lines specific routes.")

    def _prepare_report_data(self):
        data = super(StockRulesReport, self)._prepare_report_data()
        data['so_route_ids'] = self.so_route_ids.ids
        return data
