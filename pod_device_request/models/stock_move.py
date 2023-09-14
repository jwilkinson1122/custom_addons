# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    device_administration_id = fields.Many2one(
        comodel_name="pod.device.administration",
        string="Device administration event",
        ondelete="restrict",
        index=True,
    )

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields.append("device_administration_id")
        return distinct_fields
