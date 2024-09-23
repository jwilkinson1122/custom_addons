# -*- coding: utf-8 -*-
from odoo import fields, models


class PosConfig(models.Model):
    """POS configuration settings"""
    _inherit = 'pos.config'

    enable_prescriptions = fields.Boolean(string="Enable Prescription Orders", help="Enable if you want to book prescription order from pos", default=True)


 
