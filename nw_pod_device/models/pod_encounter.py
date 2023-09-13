from odoo import fields, models


class PodiatryEncounter(models.Model):
    _inherit = "pod.encounter"

    device_item_ids = fields.One2many(
        "pod.device.item",
        inverse_name="encounter_id",
        states={
            "onleave": [("readonly", True)],
            "finished": [("readonly", True)],
            "cancelled": [("readonly", True)],
        },
    )
    procurement_group_id = fields.Many2one("procurement.group", readonly=True)
    picking_ids = fields.One2many("stock.picking", inverse_name="encounter_id")

    def _add_device_vals(self, location, product, qty, is_phantom):
        return {
            "encounter_id": self.id,
            "location_id": location.id,
            "product_id": product.id,
            "qty": qty,
            "price": product.list_price,
            "is_phantom": is_phantom,
        }

    def _add_device(self, location, product, qty=1, is_phantom=False):
        return self.env["pod.device.item"].create(
            self._add_device_vals(location, product, qty, is_phantom)
        )

    def add_device(self, location, product, qty=1):
        bom = self.env["mrp.bom"].sudo()._bom_find(product=product)
        if not bom or bom.type != "phantom":
            return self._add_device(location, product, qty)
        factor = qty / bom.product_qty
        boms, lines = bom.sudo().explode(
            product, factor, picking_type=bom.picking_type_id
        )
        for bom_line, line_data in lines:
            self._add_device(location, bom_line.product_id, line_data["qty"])
        self._add_device(location, product, qty, is_phantom=True)

    def inprogress2onleave(self):
        data = {}
        for item in self.device_item_ids.filtered(lambda r: not r.is_phantom):
            product, loc_type, request = item._to_device_request(data)
            if not data.get(product, False):
                data[product] = {}
            data[product][loc_type] = request
        return super().inprogress2onleave()

    def onleave2finished(self):
        for careplan in self.careplan_ids:
            for req in careplan.device_request_ids:
                if req.state == "draft":
                    req.draft2active()
                if req.state == "active":
                    req.active2completed()
        if not self.env.context.get("no_complete_administration", False):
            self.process_device_request()
        return super().onleave2finished()

    def process_device_request(self):
        self.env["stock.immediate.transfer"].sudo().create(
            {"pick_ids": [(6, 0, self.picking_ids.ids)]}
        ).process()