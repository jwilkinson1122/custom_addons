
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # pos_prescription_order_print_ids = fields.Many2many(
    #     "ir.actions.report",
    #     related="pos_config_id.print_prescription_order_ids",
    #     readonly=False,
    # )

    pos_sale_order_print_ids = fields.Many2many(
        "ir.actions.report",
        related="pos_config_id.print_sales_order_ids",
        readonly=False,
    )
