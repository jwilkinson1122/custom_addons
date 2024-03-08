from odoo import _, api, fields, models
import datetime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _prepare_from_pos(self, order_data):
        PosSession = self.env["pos.session"]
        session = PosSession.browse(order_data["pos_session_id"])
        return {
            "partner_id": order_data["partner_id"],
            "origin": _("Point of Sale %s") % (session.name),
            "client_order_ref": order_data["name"],
            "user_id": order_data["user_id"],
            "pricelist_id": order_data["pricelist_id"],
            "fiscal_position_id": order_data["fiscal_position_id"],
        }
    
    @api.model
    def create_order_from_pos(self, order_data, action):
        SaleOrderLine = self.env["sale.order.line"]
        order_vals = self._prepare_from_pos(order_data)
        sale_order = self.create(order_vals)
        for order_line_data in order_data["lines"]:
            order_line_vals = SaleOrderLine._prepare_from_pos(sale_order, order_line_data[2])
            SaleOrderLine.create(order_line_vals)
        if action in ["confirmed", "delivered", "invoiced"]:
            sale_order.action_confirm()
        if action in ["delivered", "invoiced"]:
            for move in sale_order.mapped("picking_ids.move_ids_without_package"):
                move.quantity_done = move.product_uom_qty
            sale_order.mapped("picking_ids").button_validate()
        if action in ["invoiced"]:
            invoices = sale_order._create_invoices()
            invoices.action_post()
        return {"sale_order_id": sale_order.id}
