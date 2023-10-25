from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _set_included_options(self):
        sale_options = self.option_ids.mapped("product_option_id")
        included_option = sale_options.mapped("included_option_ids")
        to_include = included_option - sale_options
        options = []
        for opt in to_include:
            options.append((0, 0, self._prepare_sale_line_option(opt)))
        self.option_ids = options
        return to_include

    @api.onchange("option_ids")
    def option_id_change(self):
        res = {}
        if self.option_ids:
            self._set_included_options()
        return res
