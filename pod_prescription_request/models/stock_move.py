
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    prescription_administration_id = fields.Many2one(
        comodel_name="pod.prescription.administration",
        string="Prescription event",
        ondelete="restrict",
        index=True,
    )

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields.append("prescription_administration_id")
        return distinct_fields
