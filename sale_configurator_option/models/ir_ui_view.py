from odoo import models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _view_to_complete_dynamically(self):
        res = super()._view_to_complete_dynamically()
        res.append(
            (
                "tree",
                "sale_configurator_option.sale_order_line_config_option_view_form_base",
                "//field[@name='option_ids']/tree",
            )
        )
        return res
