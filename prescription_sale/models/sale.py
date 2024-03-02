# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    type = fields.Many2one('prescription.type', domain=[('sale_ok','=',True)], readonly="state not in ('draft', 'sent')")
    # type = fields.Many2one('prescription.type', domain=[('sale_ok','=',True)], readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    practitioner = fields.Many2one('res.partner', readonly="state not in ('draft', 'sent')")

    @api.onchange('type')
    def set_practitioner(self):
        if self.type and self.type.practitioner_id:
            self.practitioner = self.type.practitioner_id
        else:
            self.practitioner = False

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.picking_ids.write({'type': self.type and self.type.id, 'practitioner': self.practitioner and self.practitioner.id})
        return res
