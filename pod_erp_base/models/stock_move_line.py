# -*- coding: utf-8 -*-
from odoo import fields, models, _, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    owner_id = fields.Many2one("res.partner", string="Billing", compute="compute_owner_id", readonly=True,
                                   store=True)

    @api.depends('picking_id', 'picking_id.owner_id')
    def compute_owner_id(self):
        """
        Due to huge data of partner on live database convert this fields to compute field instead of related field
        """
        for line in self:
            line.update({'owner_id': line.picking_id.owner_id and line.picking_id.owner_id.id or False})
