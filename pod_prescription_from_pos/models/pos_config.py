from odoo import _, api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"


    create_rx = fields.Boolean("Create Prescriptions Order", help="Allow to create Prescriptions Order in POS", default=True)