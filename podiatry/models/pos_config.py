from odoo import _, api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    image = fields.Binary(string='Image')

    create_so = fields.Boolean(
        "Create Sales Order", help="Allow to create Sales Order in POS", default=True)
