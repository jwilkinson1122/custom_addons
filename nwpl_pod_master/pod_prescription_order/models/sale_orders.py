from datetime import date, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_prescription = fields.Boolean(string='Is Prescription Order')

    prescription_order_id = fields.Many2one(
        "prescription.order",
        string="Origin prescription order",
        related="order_line.prescription_order_line.order_id",
    )

    @api.model
    def _check_exchausted_prescription_order_line(self):
        return any(
            line.prescription_order_line.remaining_qty < 0.0 for line in self.order_line
        )

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            if order._check_exchausted_prescription_order_line():
                raise ValidationError(
                    _(
                        "Cannot confirm order %s as one of the lines refers "
                        "to a prescription order that has no remaining quantity."
                    )
                    % order.name
                )
        return res

    @api.constrains("partner_id")
    def check_partner_id(self):
        for line in self.order_line:
            if line.prescription_order_line:
                if line.prescription_order_line.partner_id != self.partner_id:
                    raise ValidationError(
                        _(
                            "The customer must be equal to the "
                            "prescription order lines customer"
                        )
                    )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    prescription_order_line = fields.Many2one(
        "prescription.order.line", string="Prescription Order line", copy=False
    )

    def _get_assigned_rx_line(self, rx_lines):
        # We get the prescription order line with enough quantity and closest
        # scheduled date
        assigned_rx_line = False
        date_planned = date.today()
        date_delta = timedelta(days=365)
        for line in rx_lines.filtered(lambda rx_line: rx_line.date_schedule):
            date_schedule = line.date_schedule
            if date_schedule and abs(date_schedule - date_planned) < date_delta:
                assigned_rx_line = line
                date_delta = abs(date_schedule - date_planned)
        if assigned_rx_line:
            return assigned_rx_line
        non_date_rx_lines = rx_lines.filtered(lambda rx_line: not rx_line.date_schedule)
        if non_date_rx_lines:
            return non_date_rx_lines[0]

    def _get_eligible_rx_lines_domain(self, base_qty):
        filters = [
            ("product_id", "=", self.product_id.id),
            ("remaining_qty", ">=", base_qty),
            ("currency_id", "=", self.order_id.currency_id.id),
            ("order_id.state", "=", "open"),
        ]
        if self.order_id.partner_id:
            filters.append(("partner_id", "=", self.order_id.partner_id.id))
        return filters

    def _get_eligible_rx_lines(self):
        base_qty = self.product_uom._compute_quantity(
            self.product_uom_qty, self.product_id.uom_id
        )
        filters = self._get_eligible_rx_lines_domain(base_qty)
        return self.env["prescription.order.line"].search(filters)

    def get_assigned_rx_line(self):
        self.ensure_one()
        eligible_rx_lines = self._get_eligible_rx_lines()
        if eligible_rx_lines:
            if (
                not self.prescription_order_line
                or self.prescription_order_line not in eligible_rx_lines
            ):
                self.prescription_order_line = self._get_assigned_rx_line(eligible_rx_lines)
        else:
            self.prescription_order_line = False
        self.onchange_prescription_order_line()
        return {"domain": {"prescription_order_line": [("id", "in", eligible_rx_lines.ids)]}}

    @api.onchange("product_id", "order_partner_id")
    def onchange_product_id(self):
        # If product has changed remove the relation with prescription order line
        if self.product_id:
            return self.get_assigned_rx_line()
        return

    @api.onchange("product_uom", "product_uom_qty")
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get("fiscal_position"),
            )
            self.price_unit = product._get_tax_included_unit_price(
                self.company_id or self.order_id.company_id,
                self.order_id.currency_id,
                self.order_id.date_order,
                "sale",
                fiscal_position=self.order_id.fiscal_position_id,
                product_price_unit=self._get_display_price(),
                product_currency=self.order_id.currency_id,
            )
        if self.product_id and not self.env.context.get("skip_prescription_find", False):
            return self.get_assigned_rx_line()
        return

    @api.onchange("prescription_order_line")
    def onchange_prescription_order_line(self):
        rxl = self.prescription_order_line
        if rxl:
            self.product_id = rxl.product_id
            if rxl.product_uom != self.product_uom:
                price_unit = rxl.product_uom._compute_price(
                    rxl.price_unit, self.product_uom
                )
            else:
                price_unit = rxl.price_unit
            self.price_unit = price_unit
            if rxl.taxes_id:
                self.tax_id = rxl.taxes_id
        else:
            if not self.tax_id:
                self._compute_tax_id()
            self.with_context(skip_prescription_find=True).product_uom_change()

    @api.constrains("product_id")
    def check_product_id(self):
        for line in self:
            if (
                line.prescription_order_line
                and line.product_id != line.prescription_order_line.product_id
            ):
                raise ValidationError(
                    _(
                        "The product in the prescription order and in the "
                        "sales order must match"
                    )
                )

    @api.constrains("currency_id")
    def check_currency(self):
        for line in self:
            if line.prescription_order_line:
                if line.currency_id != line.prescription_order_line.order_id.currency_id:
                    raise ValidationError(
                        _(
                            "The currency of the prescription order must match with "
                            "that of the sale order."
                        )
                    )
