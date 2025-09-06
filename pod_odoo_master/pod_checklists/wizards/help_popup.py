from odoo import fields, models


class ChecklistHelpPopup(models.TransientModel):
    _name = "pod.checklist.help.popup"
    _description = "Checklist Help Popup"

    description = fields.Text(required=True, readonly=True)

    def action_close(self):
        return {"type": "ir.actions.act_window_close"}
