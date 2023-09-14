from odoo import api, fields, models


class PrintingAction(models.Model):
    _name = "printing.action"
    _description = "Print Job Action"

    @api.model
    def _available_action_types(self):
        return [
            ("server", "Send to Printer"),
            ("client", "Send to Client"),
            ("user_default", "Use user's defaults"),
        ]

    name = fields.Char(required=True)
    action_type = fields.Selection(
        selection=_available_action_types, string="Type", required=True
    )
