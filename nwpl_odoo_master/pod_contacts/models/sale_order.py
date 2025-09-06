
import logging
import json
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    po_ref = fields.Many2one('purchase.order', string='PO Ref')
    
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
        param_value = self.env["ir.config_parameter"].sudo().get_param(
            "nwpl_odoo_master.last_no_of_days_orders", "7"
        )

        try:
            last_days = int(param_value)
            if last_days < 1:
                _logger.warning("Invalid last_no_of_days_orders: %s. Using default value 3.", last_days)
                last_days = 3  # Use a fallback value
        except ValueError:
            _logger.warning("Non-numeric value found for last_no_of_days_orders: %s. Using default value 3.", param_value)
            last_days = 3

        stages = self.env["ir.config_parameter"].sudo().get_param("nwpl_odoo_master.stages", "all")
        last_orders = int(
            self.env["ir.config_parameter"].sudo().get_param("nwpl_odoo_master.last_no_of_orders", "10")
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
        if not isinstance(n, int) or n < 1:
            _logger.warning("Invalid last_days value: %s. Using default value 3.", n)
            n = 3  # Default fallback
        today = fields.Date.today()
        return [(today - timedelta(days=i)) for i in range(n)]

    def action_delete_canceled(self):
        # allow multi selection from tree
        orders = self

        # 1) Only cancelled
        not_canceled = orders.filtered(lambda o: o.state != "cancel")
        if not_canceled:
            raise UserError(_("Only cancelled quotations/orders can be deleted."))

        # 2) Make sure related docs are also canceled/draft
        blocking = []
        for o in orders:
            bad_invoices  = o.invoice_ids.filtered(lambda m: m.state not in ("cancel", "draft"))
            bad_pickings  = o.picking_ids.filtered(lambda p: p.state not in ("cancel", "draft"))
            bad_mos       = getattr(o, 'mrp_production_ids', self.env['mrp.production']).filtered(lambda m: m.state not in ("cancel", "draft")) if hasattr(o, 'mrp_production_ids') else self.env['mrp.production']
            if bad_invoices or bad_pickings or bad_mos:
                blocking.append(o.name)
        if blocking:
            raise UserError(_(
                "You can only delete canceled orders when all related documents "
                "are also canceled (or draft).\nBlocking orders: %s"
            ) % ", ".join(blocking))
        if any(o.state == 'sale' for o in orders): 
            raise UserError(_("You cannot delete confirmed sales orders."))
        # 3) Clean dependent rows that have a required FK to sale.order
        self.env["order.history"].sudo().search([("sale_order_id", "in", orders.ids)]).unlink()

        # 4) Delete (order lines/attachments/followers will cascade)
        count = len(orders)
        orders.unlink()

        # 5) Toast
        return self.env["ir.actions.client"].create({
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Deleted"),
                "message": _("Deleted %s cancelled record(s).") % count,
                "type": "success",
                "sticky": False,
            },
        })
      
    # measurement_ids = fields.One2many('pod.measurement.group', 'sale_order_id', string='Measurements')

    # def add_measurement_category(self, measurement_values):
    #     if isinstance(measurement_values, str):
    #         try:
    #             measurement_values = json.loads(measurement_values)
    #         except json.JSONDecodeError:
    #             raise ValidationError("Invalid JSON format")

    #     if not isinstance(measurement_values, list) or not measurement_values:
    #         raise ValidationError("Invalid data format; list of dictionaries expected.")

    #     required_keys = {'date', 'category_id', 'measurement_unit', 'measurement_ids'}
    #     for values in measurement_values:
    #         if not required_keys.issubset(values.keys()):
    #             missing = required_keys - set(values.keys())
    #             raise ValidationError(f"Missing required keys: {', '.join(missing)}")

    #         measurement_cat = self.env['pod.measurement.group'].create({
    #             'date': values.get('date'),
    #             'sale_order_id': self.id,
    #             'category_id': values.get('category_id'),
    #             'measurement_unit': int(values.get('measurement_unit'))
    #         })

    #         if measurement_cat:
    #             measurements = [
    #                 {
    #                     'measurement_cat_id': measurement_cat.id,
    #                     'measurement_type': m.get('measurement_type'),
    #                     'measurement': m.get('measurement_value')
    #                 }
    #                 for m in values.get('measurement_ids', [])
    #             ]
    #             self.env['measurement.measurement'].create(measurements)

    # def get_measurements(self):
    #     measurements = []
    #     for record in self:
    #         measurement_lines = self.env['pod.measurement.group'].search([('sale_order_id', '=', record.id)])
    #         for line in measurement_lines:
    #             measurements.append({
    #                 'date': line.date,
    #                 'category': line.category_id.name,
    #                 'unit': line.measurement_unit.name,
    #                 'values': [{'id': m.id, 'name': m.measurement_type.name, 'value': m.measurement} for m in line.measurement_ids]
    #             })
    #     return measurements

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    order_line_history_ids = fields.One2many(
        "order.history", "line_id", string="Order History Lines"
    )

    # measurement_ids = fields.Many2many('measurement.measurement', string='Measurements')
    # measurement_display = fields.Char(string='Measurements Display', compute='_compute_measurement_display')
 
    # @api.depends('measurement_ids')
    # def _compute_measurement_display(self):
    #     for line in self:
    #         if line.measurement_ids:
    #             measurements = ', '.join([f"{m.measurement_type.name}: {m.measurement}" for m in line.measurement_ids])
    #             line.measurement_display = measurements
    #         else:
    #             line.measurement_display = ''