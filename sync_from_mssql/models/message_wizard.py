from odoo import models, fields


class MessageWizard(models.TransientModel):
    _name = "message.wizard"
    _description = "Message Wizard"

    message = fields.Text("Message", required=True)

    def action_confirm(self):
        return {"type": "ir.actions.act_window_close"}
