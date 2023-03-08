from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    customer_order_number_to_invoice = fields.Boolean(
        string="Pass Customer Order Number to Invoice",
        help=(
            """If checked, sale order's customer order number will be added
              to the terms and conditions freetext field on invoice"""
        ),
    )
