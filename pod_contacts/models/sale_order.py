from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    company_group_id = fields.Many2one(
        related="partner_id.company_group_id", store=True
    )

    picking_policy = fields.Selection(
        selection=lambda self: self._get_picking_policy_selection(),
        compute="_compute_picking_policy",
        store=True,
        readonly=False,
        string="Shipping Policy",
    )

    @api.depends("partner_id", "partner_shipping_id")
    def _compute_picking_policy(self):
        """Compute picking policy based on partner or shipping partner."""
        for order in self:
            order.picking_policy = (
                order.partner_shipping_id.picking_policy
                or order.partner_id.picking_policy
                or "direct"  # Default value if no policy is set
            )

    @api.model
    def _get_picking_policy_selection(self):
        """Return the available selection options for picking policy."""
        return [
            ("direct", "Deliver each product when available"),
            ("one", "Deliver all products at once"),
        ]
