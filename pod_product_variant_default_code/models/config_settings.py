from odoo import fields, models


class BaseConfiguration(models.TransientModel):
    _inherit = "res.config.settings"

    # group_product_variant = fields.Boolean("Variants", implied_group='product.group_product_variant')

    group_product_default_code_manual_mask = fields.Boolean(
        string="Product Default Code Manual Mask",
        default=False,
        help="Set behaviour of codes. Default: Automask"
        " (depends on variant use: "
        "see Sales/Purchases configuration)",
        implied_group="pod_product_variant_default_code.group_product_default_code_manual_mask",
    )

    prefix_as_default_code = fields.Boolean(
        string="Reference Prefix as default Reference",
        default=False,
        config_parameter="pod_product_variant_default_code.prefix_as_default_code",
    )
