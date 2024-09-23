# -*- coding: utf-8 -*-


from odoo import fields, models


class Posconfig(models.Model):
    _inherit = "pos.config"

    pod_allow_order_line_discount = fields.Boolean("Allow Line Discount")
    pod_allow_global_discount = fields.Boolean("Allow Global Discount")
