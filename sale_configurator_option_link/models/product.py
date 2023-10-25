from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductConfiguratorOption(models.Model):
    _inherit = "product.configurator.option"

    included_by_option_id = fields.Many2one(
        "product.configurator.option",
        "Included by Option",
        compute="_compute_included_by_option_id",
        store=True,
    )

    included_by_product_id = fields.Many2one(
        "product.product", "Included by Product", domain=[("is_option", "=", True)]
    )
    included_option_ids = fields.One2many(
        "product.configurator.option", "included_by_option_id"
    )

    @api.constrains("included_by_product_id", "included_by_option_id")
    def _check_included_by_product_id(self):
        if self.filtered(
            lambda o: o.included_by_product_id and not o.included_by_option_id
        ):
            raise ValidationError(_("Included option must be defined first"))

    @api.depends("included_by_product_id")
    def _compute_included_by_option_id(self):
        for option in self:
            options = option.product_tmpl_id.configurable_option_ids.filtered(
                lambda o: o.product_id == option.included_by_product_id
            )
            option.included_by_option_id = options and options[0] or False
