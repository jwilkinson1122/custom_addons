from odoo import api, fields, models

SALE_ORDER_STATE = [
    ("all", "ALL"),
    ("draft", "Quotation"),
    ("sent", "Quotation Sent"),
    ("sale", "Sales Order"),
    ("cancel", "Cancelled"),
]


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    last_no_of_orders = fields.Integer(string="Last No. of Orders")
    last_no_of_days_orders = fields.Integer(string="Last No. of Day's Orders")
    stages = fields.Selection(selection=SALE_ORDER_STATE, string="Stages")
    enable_reorder = fields.Boolean(string="Enable Reorder")

    def set_values(self):
        super(
            ResConfigSettings, self
        ).set_values()  # to ensure any other settings are save
        param = self.env["ir.config_parameter"]
        param.set_param(
            "nwpl_odoo_master.last_no_of_orders", str(self.last_no_of_orders)
        )
        param.set_param(
            "nwpl_odoo_master.last_no_of_days_orders", str(self.last_no_of_days_orders)
        )
        param.set_param("nwpl_odoo_master.stages", self.stages)
        param.set_param(
            "nwpl_odoo_master.enable_reorder",
            "True" if self.enable_reorder else "False",
        )
        self.env["sale.order"].search([])._compute_is_enable_reorder()

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env["ir.config_parameter"]
        res.update(
            last_no_of_orders=int(
                param.get_param("nwpl_odoo_master.last_no_of_orders", default="0")
            ),
            last_no_of_days_orders=int(
                param.get_param("nwpl_odoo_master.last_no_of_days_orders", default="0")
            ),
            stages=param.get_param("nwpl_odoo_master.stages"),
            enable_reorder=param.get_param(
                "nwpl_odoo_master.enable_reorder", default="False"
            )
            == "True",
        )
        return res
