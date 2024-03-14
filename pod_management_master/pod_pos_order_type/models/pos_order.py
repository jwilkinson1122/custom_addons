# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    pod_order_type_id = fields.Many2one('pod.order.type', string='Order Type')

    @api.model
    def _order_fields(self, ui_order):
        res = super()._order_fields(ui_order)
        res['pod_order_type_id'] = ui_order.get('pod_order_type_id', False)
        return res
