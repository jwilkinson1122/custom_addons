

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    device_administration_id = fields.Many2one(
        comodel_name="podiatry.device.administration",
        string="Prescription administration event",
        ondelete="restrict",
        index=True,
    )

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields.append("device_administration_id")
        return distinct_fields
