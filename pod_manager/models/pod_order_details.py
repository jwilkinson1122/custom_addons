# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime


class pod_order_details(models.Model):
    _name = "pod.order.line"
    _description = 'order details'

    name = fields.Many2one('pod.order', 'Order ID')
    treatment_id = fields.Many2one('pod.treatment', 'Treatment')
    diagnosis = fields.Char('Diagnosis')
    prnt = fields.Boolean('Print')
    qty = fields.Integer('x')
    quantity = fields.Integer('Quantity')
    short_comment = fields.Char('Comment', size=128)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
