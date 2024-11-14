from odoo import fields, models


class SaleConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_prescription_disable_adding_lines = fields.Boolean(
        string="Disable adding more lines to SOs",
        implied_group="nwpl_odoo_master.prescription_orders_disable_adding_lines",
    )
