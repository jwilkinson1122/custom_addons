# -*- coding: utf-8 -*-

import logging
import json
from lxml import etree
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_reorder = fields.Boolean("Is Reorder")
    is_enable_reorder = fields.Boolean(string="Enable Reorder", compute="_compute_is_enable_reorder", store=True)

    order_history_ids = fields.One2many(
        "order.history",
        "sale_order_id",
        string="Order History",
        compute="_compute_order_history_ids",
        store=True,
    )

    limited_order_history_ids = fields.One2many(
        "order.history",
        "sale_order_id",
        string="Limited Order History",
        compute="_compute_limited_order_history",
    )

    history_selection_ids = fields.One2many(
        comodel_name="order.history",
        inverse_name="sale_order_id",
        string="Selectable Order History",
    )

    use_parent_address = fields.Boolean(
        string="Use Parent Address",
        help="Enable this option to inherit the parent's delivery address."
    )

    # Related fields to fetch the parent's address
    parent_street = fields.Char(related='partner_id.parent_id.street', readonly=True)
    parent_city = fields.Char(related='partner_id.parent_id.city', readonly=True)
    parent_zip = fields.Char(related='partner_id.parent_id.zip', readonly=True)
    parent_state_id = fields.Many2one('res.country.state', related='partner_id.parent_id.state_id', readonly=True)
    parent_country_id = fields.Many2one('res.country', related='partner_id.parent_id.country_id', readonly=True)


    partner_invoice_id = fields.Many2one(
        comodel_name='res.partner',
        string="Invoice Address",
        compute='_compute_partner_invoice_id',
        store=True, readonly=False, required=True, precompute=True,
        check_company=True,
        index='btree_not_null'
    )
    
    partner_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string="Delivery Address",
        compute='_compute_partner_shipping_id',
        store=True, readonly=False, required=True, precompute=True,
        check_company=True,
        index='btree_not_null'
    )

    @api.depends('partner_id')
    def _compute_partner_invoice_id(self):
        for order in self:
            order.partner_invoice_id = (
                order.partner_id.address_get(['invoice'])['invoice']
                if order.partner_id else False
            )

    @api.depends('partner_id')
    def _compute_partner_shipping_id(self):
        for order in self:
            if order.partner_id:
                if order.partner_id.use_parent_address and order.partner_id.parent_id:
                    # Use the parent partner's delivery address
                    order.partner_shipping_id = order.partner_id.parent_id.address_get(['delivery'])['delivery']
                else:
                    # Use the current partner's delivery address
                    order.partner_shipping_id = order.partner_id.address_get(['delivery'])['delivery']
            else:
                order.partner_shipping_id = False

    @api.depends('partner_shipping_id', 'partner_id', 'company_id')
    def _compute_fiscal_position_id(self):
        """
        Trigger the change of fiscal position when the shipping address is modified.
        """
        cache = {}
        for order in self:
            if not order.partner_id:
                order.fiscal_position_id = False
                continue
            fpos_id_before = order.fiscal_position_id.id
            key = (order.company_id.id, order.partner_id.id, order.partner_shipping_id.id)
            if key not in cache:
                cache[key] = self.env['account.fiscal.position'].with_company(
                    order.company_id
                )._get_fiscal_position(order.partner_id, order.partner_shipping_id).id
            if fpos_id_before != cache[key] and order.order_line:
                order.show_update_fpos = True
            order.fiscal_position_id = cache[key]

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self._compute_partner_shipping_id()
            self._compute_partner_invoice_id()

    @api.onchange('use_parent_address', 'partner_id')
    def _onchange_use_parent_address(self):
        for order in self:
            if order.use_parent_address and order.partner_id.parent_id:
                order.partner_shipping_id = order.partner_id.parent_id
            elif not order.use_parent_address:
                order.partner_shipping_id = order.partner_id.address_get(['delivery']).get('delivery')

    @api.depends("partner_id")
    def _compute_is_enable_reorder(self):
        """Compute if reordering is enabled based on configuration."""
        param = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale.enable_reorder", "False")
        )
        enabled = param.lower() == "true"
        for record in self:
            record.is_enable_reorder = enabled

    @api.depends("partner_id")
    def _compute_order_history_ids(self):
        """Fetch full order history for the partner."""
        for record in self:
            histories = []
            if record.partner_id and isinstance(
                record.id, int
            ):  # Ensure valid record ID
                orders = self.env["sale.order"].search(
                    [("partner_id", "=", record.partner_id.id), ("id", "!=", record.id)]
                )
                for order in orders:
                    for line in order.order_line:
                        histories.append(
                            (
                                0,
                                0,
                                {
                                    "order_number": order.name,
                                    "order_date": order.date_order,
                                    "order_product": line.product_id.name,
                                    "order_price": line.price_unit,
                                    "order_quantity": line.product_uom_qty,
                                    "order_discount": line.discount,
                                    "order_sub_total": line.price_subtotal,
                                    "order_status": order.state,
                                    "sale_order_id": order.id,
                                },
                            )
                        )
            record.order_history_ids = histories

    @api.depends("order_history_ids")
    def _compute_limited_order_history(self):
        """Fetch limited order history based on configurable constraints."""
        last_days = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("pod_partner_hierarchy.last_no_of_days_orders", "3")
        )
        stages = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("pod_partner_hierarchy.stages", "all")
        )
        last_orders = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("pod_partner_hierarchy.last_no_of_orders", "10")
        )
        recent_dates = self.get_recent_dates(last_days)

        for record in self:
            if not isinstance(record.id, int):  # Skip unsaved records
                record.limited_order_history_ids = []
                continue

            filtered_history = [
                line
                for line in record.order_history_ids
                if line.order_date.date() in recent_dates
                and (stages == "all" or line.order_status == stages)
            ]
            record.limited_order_history_ids = [
                (6, 0, [line.id for line in filtered_history[:last_orders]])
            ]

    def action_reorder(self):
        """Create a reorder based on selected history items."""
        self.ensure_one()
        if not self.is_enable_reorder:
            raise UserError(_("Reordering is disabled by configuration."))

        new_order = self.copy(
            default={
                "name": self.env["ir.sequence"].next_by_code("sale.order"),
                "is_reorder": True,
            }
        )
        selected_histories = self.history_selection_ids.filtered(
            lambda h: h.order_status == "sale"
        )

        order_lines = [
            (
                0,
                0,
                {
                    "product_id": history.product_id.id,
                    "name": history.product_id.name,
                    "product_uom_qty": history.order_quantity,
                    "price_unit": history.order_price,
                },
            )
            for history in selected_histories
        ]

        new_order.write({"order_line": order_lines})

        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "view_mode": "form",
            "res_id": new_order.id,
            "target": "current",
        }

    def button_all_history_add_to_order(self):
        """Add all limited history items as order lines."""
        self.ensure_one()

        # Ensure there are limited history items to process
        if not self.limited_order_history_ids:
            raise ValidationError(_("No items in limited order history to add."))

        order_lines = []
        for history in self.limited_order_history_ids:
            # Find the product based on the product name in the history
            product = self.env["product.product"].search(
                [("name", "=", history.order_product)], limit=1
            )

            if not product:
                _logger.warning(
                    f"Product '{history.order_product}' not found. Skipping."
                )
                continue

            # Prepare values for the sale order line
            line_values = {
                "order_id": self.id,
                "product_id": product.id,
                "name": history.order_product,
                "product_uom_qty": history.order_quantity or 1.0,
                "price_unit": history.order_price or 0.0,
                "discount": history.order_discount or 0.0,
            }

            # Append to the list of lines
            order_lines.append((0, 0, line_values))

        # Check if any lines were created
        if not order_lines:
            raise ValidationError(
                _("No valid products were found to add to the order.")
            )

        # Write the order lines to the current order
        self.write({"order_line": order_lines})

        _logger.info(f"Added {len(order_lines)} order lines to sale order {self.name}.")

        return True

    def action_open_sale_order(self):
        """Open the current sale order in a form view."""
        self.ensure_one()
        return {
            "name": _("Sale Order"),
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "view_mode": "form",
            "res_id": self.id,
            "target": "current",
        }

    def get_recent_dates(self, n):
        """Return a list of recent dates."""
        if n < 1:
            raise ValueError("Number of days must be greater than 0.")
        today = fields.Date.today()
        return [(today - timedelta(days=i)) for i in range(n)]

    

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    order_line_history_ids = fields.One2many(
        "order.history", "line_id", string="Order History Lines"
    )
