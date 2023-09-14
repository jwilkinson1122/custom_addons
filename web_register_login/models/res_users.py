

from odoo import fields, models


class ResUsers(models.Model):

    _inherit = "res.users"

    dont_register_login = fields.Boolean()

    def register_new_login(self):
        return self.env["res.users.access.log"].create({})  # populated by defaults

    def _update_last_login(self):
        super()._update_last_login()
        if not self.dont_register_login:
            self.register_new_login()

    def view_access_registers(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "web_register_login.res_users_access_log_act_window"
        )
        action["domain"] = [("create_uid", "=", self.id)]
        return action
