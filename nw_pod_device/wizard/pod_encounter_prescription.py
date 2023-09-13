from odoo import fields, models


class PodiatryCareplanDevice(models.TransientModel):
    _name = "pod.encounter.device"
    _description = "pod.encounter.device"

    pod_id = fields.Many2one("pod.encounter", required=True, readonly=True)
    product_id = fields.Many2one(
        "product.product",
        required=True,
        domain=[("type", "in", ["consu", "product"])],
    )
    location_id = fields.Many2one(
        "res.partner",
        domain=[
            ("stock_location_id", "!=", False),
            ("is_location", "=", True),
        ],
        required=True,
    )

    def run(self):
        return self.pod_id.add_device(self.location_id, self.product_id)
