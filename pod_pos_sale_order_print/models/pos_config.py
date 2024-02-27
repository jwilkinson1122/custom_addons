from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    # print_prescription_order_ids = fields.Many2many(
    #     "ir.actions.report",
    #     "pos_config_ir_actions_report_rel",
    #     "pos_config_id",
    #     "report_id",
    #     string="Print Prescription Orders",
    #     domain="[('model', '=', 'prescription.order')]",
    #     help="Print multiple Prescription Orders in POS",
    # )

    print_sales_order_ids = fields.Many2many(
        "ir.actions.report",
        "pos_config_ir_actions_report_rel",
        "pos_config_id",
        "report_id",
        string="Print Sales Orders",
        domain="[('model', '=', 'sale.order')]",
        help="Print multiple Sale Orders in POS",
    )
