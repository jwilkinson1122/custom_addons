

from odoo import fields, models


class ResUsers(models.Model):

    _inherit = "res.users"

    current_signature_id = fields.Many2one("res.users.signature", readonly=True)
    digital_signature = fields.Binary(
        related="current_signature_id.signature", readonly=True
    )

    def update_signature(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "pod_signature_storage.res_users_update_signature_act_window"
        )
        action["context"] = {
            "default_user_id": self.id,
        }
        return action
