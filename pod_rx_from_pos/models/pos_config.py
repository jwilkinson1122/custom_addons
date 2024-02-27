from odoo import _, api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"


    create_rx = fields.Boolean("Create Prescription Order", help="Allow to create Prescription Order in POS", default=True)