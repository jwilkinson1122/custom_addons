from odoo import _, fields, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    option_area_id = fields.Many2one("product.configurator.option.area", "Area")

    def _get_product_option(self):
        options = super()._get_product_option()
        if self.option_area_id:
            options = options.filtered(lambda o: o.area_id == self.option_area_id)
        if len(options) > 1 and not self.option_area_id:
            raise UserError(_("Please select an Area before"))
        return options
