from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    keep_name_so = fields.Boolean(
        string="Use Same Enumeration",
        help="If this is unchecked, quotations use a different sequence from "
        "sale orders",
        default=True,
    )

    display_discount_with_tax = fields.Boolean(string="Show the Discount with TAX")
    report_total_without_discount = fields.Boolean()



class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    keep_name_so = fields.Boolean(
        related="company_id.keep_name_so",
        readonly=False,
    )

    display_discount_with_tax = fields.Boolean(
        string="Show the Discount with TAX",
        help="Check this field to show the Discount with TAX",
        related="company_id.display_discount_with_tax",
        readonly=False,
    )
    report_total_without_discount = fields.Boolean(
        string="Report Total Without Discount",
        help='Display "Total without discount" in report',
        related="company_id.report_total_without_discount",
        readonly=False,
    )
