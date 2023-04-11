# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class InheritedSaleOrder(models.Model):
    _inherit = 'account.move'

    def _compute_amount_in_word(self):
        for rec in self:
            rec.num_word = str(
                rec.currency_id.amount_to_text(rec.amount_total))

    num_word = fields.Char(
        string="This sale order is approved for the sum of: ", compute='_compute_amount_in_word')

    def print_invoice_report(self):
        return {
            'type': 'ir.actions.report',
            'report_name': "podiatry.invoice_report",
            'report_file': "podiatry.invoice_report",
            'report_type': 'qweb-pdf',
        }
