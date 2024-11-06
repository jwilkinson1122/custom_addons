# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    """inherited invoice report"""

    _inherit = "account.invoice.report"

    practice_id = fields.Many2one("res.practice", "Practice", readonly=True)

    def _select(self):
        """select"""
        return (
            super(AccountInvoiceReport, self)._select()
            + ", move.practice_id as practice_id"
        )

    # def _group_by(self):
    #     """group by"""
    #     return super(AccountInvoiceReport, self)._group_by() + \
    #            ", move.practice_id"
