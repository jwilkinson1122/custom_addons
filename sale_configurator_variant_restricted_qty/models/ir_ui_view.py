from odoo import models

from odoo.addons.sale_configurator_variant.models.ir_ui_view import XMLID

SKIP_FIELDS = [
    "sale_min_qty",
    "sale_max_qty",
    "qty_warning_message",
    "qty_invalid",
]


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _get_sale_line_tree_item(self):
        items = super()._get_sale_line_tree_item()
        if self.id == self.env["ir.model.data"].xmlid_to_res_id(XMLID):
            return [item for item in items if item.get("name") not in SKIP_FIELDS]
        return items
