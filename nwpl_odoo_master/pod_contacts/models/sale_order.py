from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta


# class SaleOrder(models.Model):
#     _inherit = "sale.order"

#     @api.model_create_multi
#     def create(self, vals_list):
#         res = super().create(vals_list)
#         for record in res:
#             partners = record.partner_id | record.partner_id.commercial_partner_id
#             partners._increase_rank("customer_rank")
#         return res

class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_reorder = fields.Boolean("Is Reorder")

    is_enable_reorder = fields.Boolean(
        string="Enable Reorder", compute="_compute_is_enable_reorder", store=True
    )

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
            .get_param("nwpl_odoo_master.last_no_of_days_orders", "3")
        )
        stages = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("nwpl_odoo_master.stages", "all")
        )
        last_orders = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("nwpl_odoo_master.last_no_of_orders", "10")
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

    # def get_recent_dates(self, n):
    #     """Return a list of recent dates."""
    #     today = fields.Date.today()
    #     return [(today - timedelta(days=i)) for i in range(n)]

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
