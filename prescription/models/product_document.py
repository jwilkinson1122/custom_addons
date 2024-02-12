

from odoo import fields, models


class ProductDocument(models.Model):
    _inherit = 'product.document'

    attached_on = fields.Selection(
        selection=[
            ('quotation', "Draft Rx"),
            ('prescription', "Confirmed order"),
        ],
        string="Visible at",
        help="Allows you to share the document with your customers within a prescription.\n"
            "Leave it empty if you don't want to share this document with prescription customer.\n"
            "Draft Rx: the document will be sent to and accessible by customers at any time.\n"
                "e.g. this option can be useful to share Product description files.\n"
            "Confirmed order: the document will be sent to and accessible by customers.\n"
                "e.g. this option can be useful to share User Manual or digital content bought"
                " on ecommerce. ",
    )
