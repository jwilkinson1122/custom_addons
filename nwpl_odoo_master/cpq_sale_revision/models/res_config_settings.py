# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfig(models.TransientModel):
    """Inherit the base settings to add a sale quotation revision field"""

    _inherit = "res.config.settings"

    is_quotation_revision = fields.Boolean(
        string="Sale Revision",
        help="Allow user to revise the sale quotations.",
        config_parameter="nwpl_odoo_master.is_quotation_revision",
    )
