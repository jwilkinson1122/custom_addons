# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
import logging
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    assigned_config = fields.Many2many(
        "pos.config", string=" Assigned Config")
    sequence_number = fields.Integer(
        string='Sequence Number ', help='A session-unique sequence number for the order', default=1)
    pod_uid = fields.Char(string='Number')
    pod_order_line_id = fields.Char(string='Line Number')
    pod_order_date = fields.Char(string="Order Date")

    @api.model
    def create_from_ui(self, orders, draft=False):
        results = super().create_from_ui(orders, draft)
        if results:
            order_ids = list(map(lambda x: x.get('id'), results))
            
            return self.env['pos.order'].search_read(domain=[('id', 'in', order_ids)], fields=['id', 'pos_reference', 'account_move', 'name', 'lines'], load=False)
        else:
            return results

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res['pod_uid'] = ui_order.get('pod_uid', False)
        res['pod_order_line_id'] = ui_order.get('pod_order_line_id', False)
        res['pod_order_date'] = ui_order.get('pod_order_date', False)
        return res


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    pod_line_id = fields.Char(string='Number')

