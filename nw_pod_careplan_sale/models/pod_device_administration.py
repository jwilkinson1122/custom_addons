from odoo import api, fields, models


class PodiatryDeviceAdministration(models.Model):
    _inherit = "pod.device.administration"

    amount = fields.Float()

    @api.model
    def create(self, vals):
        if "amount" not in vals:
            vals["amount"] = (
                self.env["product.product"].browse(vals["product_id"]).list_price
                * vals["qty"]
            )
        return super().create(vals)
