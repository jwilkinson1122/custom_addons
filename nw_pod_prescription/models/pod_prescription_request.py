from odoo import fields, models


class PodiatryPrescriptionRequest(models.Model):
    _inherit = "pod.prescription.request"

    location_type_id = fields.Many2one(
        "pod.location.type", readonly=True, tracking=True
    )

    def _get_event_values(self):
        res = super()._get_event_values()
        if self.env.context.get("product_id", False):
            res["product_id"] = self.env.context.get("product_id")
            res["product_uom_id"] = self.env.context.get("product_uom_id")
            res["qty"] = self.env.context.get("qty", 1)
            res["amount"] = self.env.context.get("amount", 0)
        if self.env.context.get("location_id", False):
            res["location_id"] = self.env.context.get("location_id")
        if self.env.context.get("stock_location_id", False):
            res["stock_location_id"] = self.env.context.get("stock_location_id")
        return res

    def _add_prescription_item(self, item):
        if self.state == "draft":
            self.draft2active()
        administration = self.with_context(
            product_id=item.product_id.id,
            product_uom_id=item.product_id.uom_id.id,
            qty=item.qty,
            amount=item.price * item.qty,
            location_id=item.location_id.id,
            tracking_disable=True,
            stock_location_id=item.location_id.stock_location_id.id,
        ).generate_event()
        administration.preparation2in_progress()
        if not self.env.context.get("no_complete_administration", False):
            administration.with_context(no_post_move=True).in_progress2completed()
        return administration
