from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    presale_order = fields.Many2one("presale.order", string="Presale order")

    presale_name = fields.Char(related="presale_order.name")
    presale_partner_id = fields.Many2one(related="presale_order.partner_id")
    presale_order_line_ids = fields.One2many(related="presale_order.order_line_ids")
