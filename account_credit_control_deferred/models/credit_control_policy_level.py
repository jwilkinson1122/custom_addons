

from odoo import fields, models


class CreditControlPolicyLevel(models.Model):

    _inherit = "credit.control.policy.level"

    channel = fields.Selection(
        selection_add=[("email_deferred", "Email Deferred")],
        ondelete={"email_deferred": "cascade"},
    )
