

from odoo import fields, models


class PodiatryRequestGroupUncheckAuthorization(models.TransientModel):

    _name = "pod.request.group.uncheck.authorization"
    _description = "Uncheck authorization"

    request_group_id = fields.Many2one("pod.request.group", required=True)

    def run(self):
        return (
            self.env["pod.request.group.check.authorization"]
            .create({"authorization_checked": False})
            .run()
        )
