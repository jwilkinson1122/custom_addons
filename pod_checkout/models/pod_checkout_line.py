from odoo import api, exceptions, fields, models


class CheckoutLine(models.Model):
    _name = "pod.checkout.line"
    _description = "Checkout Request Line"

    checkout_id = fields.Many2one("pod.checkout", required=True)
    item_id = fields.Many2one("pod.item", required=True)
    note = fields.Char("Notes")
    item_cover = fields.Binary(related="item_id.image")
