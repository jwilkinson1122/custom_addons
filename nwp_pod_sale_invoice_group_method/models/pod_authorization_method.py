# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PodiatryAuthorizationMethod(models.Model):

    _inherit = "pod.authorization.method"

    force_item_authorization_method = fields.Boolean()
