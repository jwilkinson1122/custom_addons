

from odoo import fields, models


class PodiatryAuthorizationWeb(models.Model):

    _name = "pod.authorization.web"
    _description = "Authorization Web"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    link = fields.Char()
    notes = fields.Text()
    authorization_method_ids = fields.One2many(
        "pod.authorization.method",
        inverse_name="authorization_web_id",
        readonly=True,
    )
