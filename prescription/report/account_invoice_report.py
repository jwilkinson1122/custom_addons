# -*- coding: utf-8 -*-


from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    team_id = fields.Many2one(comodel_name='crm.team', string="Prescription Team")

    def _select(self):
        return super()._select() + ", move.team_id as team_id"
