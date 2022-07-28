# -*- coding: utf-8 -*-
import datetime
import logging

from odoo import api, fields, models, _
from datetime import date, datetime

_logger = logging.getLogger(__name__)


class pod_rx_order_line(models.Model):
    _name = "pod.rx.order.line"
    _description = 'podiatry rx line'

    name = fields.Many2one('pod.rx.order', 'Rx Order ID')
    treatment_id = fields.Many2one('pod.treatment', 'Device')
    left_treatment_id = fields.Many2one('pod.treatment', 'Left Device')
    form = fields.Char('Form')
    prnt = fields.Boolean('Print')
    qty = fields.Integer('x')
    quantity = fields.Integer('Quantity')
    short_comment = fields.Char('Comment', size=128)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
