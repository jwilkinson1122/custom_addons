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

    # picking_policy = fields.Selection(
    #     compute="_compute_picking_policy", store=True, readonly=False
    # )

    @api.depends("partner_id", "partner_shipping_id")
    def _compute_picking_policy(self):
        for order in self:
            order.picking_policy = (
                order.partner_shipping_id.picking_policy
                or order.partner_id.picking_policy
                or "direct"  # Default to 'direct' or any valid value
            )

    # @api.depends("partner_id")
    # def _compute_picking_policy(self):
    #     for this in self:
    #         picking_policy = (
    #             this.partner_shipping_id.picking_policy
    #             or this.partner_id.picking_policy
    #             or self.default_get(["picking_policy"]).get("picking_policy")
    #         )
    #         this.picking_policy = picking_policy

    # @api.model
    # def _get_picking_policy_selection(self):
    #     """Retrieve the selection values for picking_policy."""
    #     return self.fields_get(["picking_policy"])["picking_policy"]["selection"]

    @api.model
    def _get_picking_policy_selection(self):
        """Retrieve the selection values for picking_policy."""
        return self.env["sale.order"].fields_get(["picking_policy"])["picking_policy"][
            "selection"
        ]
