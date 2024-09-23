# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PodCashInOut(models.Model):
    _name = 'pod.cash.in.out'
    _description = "Cash In Out"

    pod_transaction_type = fields.Selection(
        [('cash_in', 'Cash In'), ('cash_out', 'Cash Out')], string="Transaction Type",)
    pod_amount = fields.Float(string="Amount")
    pod_reason = fields.Char(string="Reason")
    pod_session = fields.Many2one('pos.session', string="Session")
    pod_date = fields.Datetime(
        string='Date', readonly=True, index=True, default=fields.Datetime.now)

    @api.model
    def try_cash_in_out(self, session, _type, amount, reason):
        if _type == 'in':
            self.env['pod.cash.in.out'].create(
                {'pod_amount': amount, 'pod_reason': reason, 'pod_session': session, 'pod_transaction_type': 'cash_in'})
        else:
            self.env['pod.cash.in.out'].create(
                {'pod_amount': amount, 'pod_reason': reason, 'pod_session': session, 'pod_transaction_type': 'cash_out'})
