from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    cpq_code_prefix = fields.Char(
        string="CPQ Default Code Prefix",
        default="CPQ-",
        config_parameter="cpq.default_code_prefix",
        help="Prefix to use for CPQ product internal references (e.g., CPQ-, ORTHO-, CUSTOM-)."
    )

    cpq_code_preview = fields.Char(
        string="CPQ Reference Preview",
        compute="_compute_cpq_code_preview"
    )

    @api.depends("cpq_code_prefix")
    def _compute_cpq_code_preview(self):
        for config in self:
            next_seq = self.env["ir.sequence"].sudo().next_by_code("product.product.default_code.cpq")
            if next_seq:
                config.cpq_code_preview = f"{config.cpq_code_prefix or ''}{next_seq.split('-')[-1]}"
            else:
                config.cpq_code_preview = f"{config.cpq_code_prefix or 'CPQ-'}00001"