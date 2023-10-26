# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.tools import float_round


class PrescriptionCashMove(models.Model):
    """ Two types of cashmoves: payment (credit) or order (debit) """
    _name = 'prescription.cashmove'
    _description = 'Prescription Cashmove'
    _order = 'date desc'

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, required=True)
    user_id = fields.Many2one('res.users', 'User',
                              default=lambda self: self.env.uid)
    date = fields.Date('Date', required=True, default=fields.Date.context_today)
    amount = fields.Float('Amount', required=True)
    description = fields.Text('Description')

    def name_get(self):
        return [(cashmove.id, '%s %s' % (_('Prescription Cashmove'), '#%d' % cashmove.id)) for cashmove in self]

    @api.model
    def get_wallet_balance(self, user, include_config=True):
        result = float_round(sum(move['amount'] for move in self.env['prescription.cashmove.report'].search_read(
            [('user_id', '=', user.id)], ['amount'])), precision_digits=2)
        if include_config:
            result += user.company_id.prescription_minimum_threshold
        return result
