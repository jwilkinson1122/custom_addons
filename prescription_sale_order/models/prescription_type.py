from odoo import fields, models


class PrescriptionType(models.Model):

    _inherit = "prescription.type"

    create_sale_order = fields.Boolean(
        string="Create sale order?",
        default=False,
    )
