from odoo import fields, models


class PodiatryAuthorizationMethod(models.Model):
    _inherit = "pod.authorization.method"

    invoice_group_method_id = fields.Many2one( string="Invoice Group Method", comodel_name="invoice.group.method",
    )
