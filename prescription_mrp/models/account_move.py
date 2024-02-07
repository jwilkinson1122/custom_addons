# -*- coding: utf-8 -*-


from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_stock_valuation_layers(self, move):
        """ Do not handle the invoice correction for kit. It has to be done
        manually """
        layers = super()._get_stock_valuation_layers(move)
        return layers.filtered(lambda svl: svl.product_id == self.product_id)
