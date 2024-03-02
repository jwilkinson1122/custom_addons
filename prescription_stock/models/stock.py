# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    type = fields.Many2one('prescription.type', domain=[('picking_ok','=',True)])
    practitioner = fields.Many2one('res.partner')
    measure = fields.Float('Kilométrage', related='type.measure', store=True, readonly=False)
    
    @api.onchange('type')
    def set_practitioner(self):
        if self.type and self.type.practitioner_id:
            self.practitioner = self.type.practitioner_id
        else:
            self.practitioner = False

class StockMove(models.Model):
    _inherit = 'stock.move'
    type = fields.Many2one('prescription.type', related='picking_id.type', store=True, readonly=True)
    practitioner = fields.Many2one('res.partner', related='picking_id.practitioner', store=True, readolny=True)
    measure = fields.Float('Kilométrage', related='picking_id.measure', store=True, readolny=True)
