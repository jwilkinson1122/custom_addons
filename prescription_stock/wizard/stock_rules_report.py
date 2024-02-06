# -*- coding: utf-8 -*-


from odoo import api, fields, models


class StockRulesReport(models.TransientModel):
    _inherit = 'stock.rules.report'

    # device_options_ids = fields.Many2many(
    #     "prescription.device.options", string="Device Options", help="List of device options."
    # )

    # attachment_ids = fields.Many2many('ir.attachment', 'patient_ir_attachments_rel',
    #                                   'manager_id', 'attachment_id', string="Attachments",
    #                                   help="Patient Image / File Attachments")

    rx_route_ids = fields.Many2many('stock.route', 'stock_rx_route_rel',
                                      'manager_id', 'route_id', string="Attachments",
                                      domain="[('prescription_selectable', '=', True)]",
                                      help="Choose to apply RX lines specific routes.")

    # rx_route_ids = fields.Many2many('stock.route', string='Apply specific routes',
    #     domain="[('prescription_selectable', '=', True)]", help="Choose to apply RX lines specific routes.")

    def _prepare_report_data(self):
        data = super(StockRulesReport, self)._prepare_report_data()
        data['rx_route_ids'] = self.rx_route_ids.ids
        return data
