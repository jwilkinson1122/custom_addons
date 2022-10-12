from odoo import api, exceptions, fields, models


class CheckoutLine(models.Model):
    _name = "podiatry.checkout.line"
    _description = "Checkout Request Line"

    checkout_id = fields.Many2one("podiatry.checkout", required=True)
    prescription_id = fields.Many2one("podiatry.prescription", required=True)
    note = fields.Char("Notes")
    prescription_cover = fields.Binary(related="prescription_id.image")
