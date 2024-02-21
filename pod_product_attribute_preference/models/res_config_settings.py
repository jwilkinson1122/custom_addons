from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    new_attribute_preference_for_all_companies = fields.Boolean(
        config_parameter=(
            "pod_product_attribute_preference."
            "product_attribute_enable_for_all_companies"
        ),
        string="Set new attribute as preference for all companies",
        help="""When a new attribute is created,
        set it as preference for all companies.
        Otherwise it is only set as preference for the user's current company""",
    )

    new_attribute_value_preference_for_all_companies = fields.Boolean(
        config_parameter=(
            "pod_product_attribute_preference."
            "product_attribute_value_enable_for_all_companies"
        ),
        string="Set new attributes value as preference for all companies",
        help="""When a new attribute value is created,
        set it as preference for all companies.
        Otherwise it is only set as preference for the user's current company""",
    )
