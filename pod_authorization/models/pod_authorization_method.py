from odoo import fields, models


class PodiatryAuthorizationMethod(models.Model):
    _inherit = "pod.authorization.method"

    check_required = fields.Boolean(default=False)
