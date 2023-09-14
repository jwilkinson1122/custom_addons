from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    requires_approval = fields.Boolean(default=False)

    def closed_states(self):
        res = super(PosConfig, self).closed_states()
        res.append("pending_approval")
        return res
