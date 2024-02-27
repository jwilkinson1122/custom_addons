# -*- coding: utf-8 -*-


from odoo import _, api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"


    create_mrp_order = fields.Boolean("Create MRP Order", help="Allow to create MRP Order in POS", default=True)
    is_done = fields.Boolean("Done MRP Order", help="Allow to Done MRP Order in POS", default=True)