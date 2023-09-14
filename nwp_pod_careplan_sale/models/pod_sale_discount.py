from odoo import fields, models


class PodiatrySaleDiscount(models.Model):
    _name = "pod.sale.discount"
    _description = "Podiatry Discounts"

    name = fields.Char(required=True)
    description = fields.Char()
    is_fixed = fields.Boolean(default=False)
    percentage = fields.Float(default=0.0, digits="Discount")
    active = fields.Boolean(default=True)
