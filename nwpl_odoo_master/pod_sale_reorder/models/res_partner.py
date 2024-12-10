# -*- coding : utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_order_ids = fields.One2many(
        "sale.order",
        "partner_id",
        string="Sale Orders",
    )

    current_sale_order_ids = fields.One2many(
        "sale.order",
        compute="_compute_current_sale_order_ids",
        string="Current Orders",
        store=False,
    )

    historic_sale_order_ids = fields.One2many(
        "sale.order",
        compute="_compute_historic_sale_order_ids",
        string="Historic Orders",
        store=False,
    )

    reorder_count = fields.Integer(
        compute="_compute_reorder_order_count",
        string="Reorder",
    )

    def _compute_current_sale_order_ids(self):
        """
        Compute method to populate the 'current_sale_order_ids' field.
        Includes all sales orders that are not done or canceled.
        """
        for partner in self:
            partner.current_sale_order_ids = partner.sale_order_ids.filtered(
                lambda order: order.state not in ("done", "cancel")
            )

    def _compute_historic_sale_order_ids(self):
        """
        Compute method to populate the 'historic_sale_order_ids' field.
        Includes all sales orders that are done or canceled and can be reordered.
        """
        for partner in self:
            partner.historic_sale_order_ids = partner.sale_order_ids.filtered(
                lambda order: order.state in ("done", "cancel") and order.is_reorder
            )

    def _compute_reorder_order_count(self):
        """
        Compute the count of reorderable historic sale orders for the partner.
        """
        for partner in self:
            partner.reorder_count = len(partner.historic_sale_order_ids)

    def open_sale_from_view_action(self):
        """
        Open the sale orders action filtered by reorder sales for the partner.
        """
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action["domain"] = [
            ("partner_id", "=", self.id),
            ("state", "=", "sale"),
            ("is_reorder", "=", True),
        ]
        return action
