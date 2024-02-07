

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    prescription_count = fields.Integer(
        string="Prescription count",
        compute="_compute_prescription_count",
    )

    def _compute_prescription_count(self):
        for rec in self:
            rec.prescription_count = len(rec.move_ids.mapped("prescription_ids"))

    def copy(self, default=None):
        self.ensure_one()
        if self.env.context.get("set_prescription_picking_type"):
            location_dest_id = default.get("location_dest_id")
            if location_dest_id:
                warehouse = self.env["stock.warehouse"].search(
                    [("prescription_loc_id", "parent_of", location_dest_id)], limit=1
                )
                if warehouse:
                    default["picking_type_id"] = warehouse.prescription_in_type_id.id
        return super().copy(default)

    def action_view_prescription(self):
        self.ensure_one()
        action = self.sudo().env.ref("prescription.prescription_action").read()[0]
        prescription = self.move_ids.mapped("prescription_ids")
        if len(prescription) == 1:
            action.update(
                res_id=prescription.id,
                view_mode="form",
                view_id=False,
                views=False,
            )
        else:
            action["domain"] = [("id", "in", prescription.ids)]
        return action
