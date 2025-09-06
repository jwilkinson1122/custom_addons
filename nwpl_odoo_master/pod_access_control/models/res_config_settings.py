from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    auth_signup_uninvited = fields.Selection(
        selection=[
            ("b2b", "On invitation"),
            ("b2c", "Free sign up"),
        ],
        string="Customer Account",
        default="b2b",
        config_parameter="auth_signup.invitation_scope",
    )
