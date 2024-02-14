# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PreviousServiceHistory(models.Model):
    """Previous Service History"""
    _name = 'previous.service.history'
    _description = __doc__
    _rec_name = 'orthotic_repair_service_id'

    orthotic_repair_service_id = fields.Many2one('product.product', string="Service Type", required=True,
                                                domain=[('is_repair_service', '=', True)])
    technician_id = fields.Many2one('res.users', string="Technician")
    date_of_service = fields.Date(string="Date of Service")
    previous_service_description = fields.Char(string="Description", translate=True)
    orthotic_repair_order_id = fields.Many2one('orthotic.repair.order', string="MRO")
