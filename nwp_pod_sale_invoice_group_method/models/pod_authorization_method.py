

from odoo import fields, models


class PodiatryAuthorizationMethod(models.Model):

    _inherit = "pod.authorization.method"

    force_item_authorization_method = fields.Boolean()
