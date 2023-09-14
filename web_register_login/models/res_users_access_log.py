

from odoo import api, fields, models


class ResUsersAccessLog(models.Model):

    _name = "res.users.access.log"
    _description = "Res Users Access Log"

    @api.model
    def _default_remote_id(self):
        return self.remote.id

    @api.model
    def _default_remote_name(self):
        return self.remote.name

    @api.model
    def _default_remote_ip(self):
        return self.remote.ip

    remote_id = fields.Many2one(
        "res.remote", readonly=True, default=lambda r: r._default_remote_id()
    )

    remote_name = fields.Char(readonly=True, default=lambda r: r._default_remote_name())

    remote_ip = fields.Char(
        readonly=True,
        string="Remote IP",
        default=lambda r: r._default_remote_ip(),
    )
