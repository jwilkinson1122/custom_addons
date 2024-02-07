
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    show_full_page_sale_prescription = fields.Boolean(
        string="Full page Prescription creation",
        help="From the frontend sale order page go to a single Prescription page "
        "creation instead of the usual popup",
    )
