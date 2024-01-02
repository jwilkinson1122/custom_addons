from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class SaleOrder(models.Model):

    _inherit = "sale.order"

    prescription_order_ids = fields.Many2many(
        comodel_name="prescription.order",
        string="Prescription orders",
        compute="_compute_prescription_order",
    )
    prescription_order_count = fields.Integer(
        string="Prescription orders count",
        compute="_compute_prescription_order",
    )

    def _compute_prescription_order(self):
        for rec in self:
            rec.prescription_order_ids = rec.mapped(
                "order_line.prescription_line_ids.prescription_id"
            ).ids
            rec.prescription_order_count = len(rec.prescription_order_ids)

    def action_show_prescription_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "prescription.action_prescription_order_tree"
        )
        form_view = [(self.env.ref("prescription.view_prescription_order_form").id, "form")]
        orders = self.mapped("prescription_order_ids")
        if len(orders) == 1:
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = orders.ids[0]
        else:
            action["domain"] += [("id", "in", orders.ids)]
            domain = safe_eval(action["domain"]) or []
            domain += [("id", "in", orders.ids)]
            action["domain"] = action["domain"]
        return action

    def _change_prescription_order_status_done(self):
        for prescription_order in self.mapped("prescription_order_ids"):
            prescription_order.write(
                {
                    "state": "done",
                }
            )

    def _change_prescription_order_status_confirmed(self):
        for prescription_order in self.mapped("prescription_order_ids"):
            prescription_order.write(
                {
                    "state": "confirmed",
                }
            )

    def action_confirm(self):
        res = super().action_confirm()
        self._change_prescription_order_status_done()
        return res

    def action_cancel(self):
        res = super().action_cancel()
        self._change_prescription_order_status_confirmed()
        return res


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    prescription_line_ids = fields.One2many(
        comodel_name="prescription.line",
        inverse_name="sale_line_id",
        string="Prescription lines",
        required=False,
    )

    def _prepare_procurement_values(self, group_id=False):
        res = super()._prepare_procurement_values(group_id)
        res.update(
            {
                "prescription_ids": self.prescription_line_ids.mapped("prescription_id.id"),
            }
        )
        return res
