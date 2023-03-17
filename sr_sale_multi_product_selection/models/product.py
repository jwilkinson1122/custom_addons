# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

from odoo import fields, models, api


class SrCreateQuotation(models.TransientModel):
    _name = "sr.create.quotation"

    partner_id = fields.Many2one('res.partner', string="Partner")

    def create_quotation(self):
        sale_id = self.env['sale.order'].create({'partner_id': self.partner_id.id})
        for product in self._context.get('active_ids'):
            self.env['sale.order.line'].create({'product_id': product,
                                                'order_id': sale_id.id})

        action = self.env.ref('sale.action_quotations').read()[0]
        action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        action['res_id'] = sale_id.ids[0]
        return action
