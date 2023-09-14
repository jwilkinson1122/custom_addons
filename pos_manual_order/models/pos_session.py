from odoo import _, models
from odoo.exceptions import ValidationError


class PosSession(models.Model):
    _inherit = "pos.session"

    def _get_manual_order_vals(
        self, product, qty, price, discount, partner, fiscal_position
    ):
        return {
            "company_id": self.config_id.company_id.id,
            "session_id": self.id,
            "pricelist_id": self.config_id.pricelist_id.id,
            "partner_id": partner.id or False,
            "fiscal_position_id": fiscal_position.id or False,
        }

    def _get_manual_order_line_vals(self, product, qty, price, discount, order):
        return [
            {
                "order_id": order.id,
                "name": self.env["ir.sequence"].next_by_code("pos.order.line"),
                "product_id": product.id,
                "price_unit": price,
                "discount": discount or 0.0,
                "tax_ids": [
                    (4, tx.id)
                    for tx in product.taxes_id.filtered(
                        lambda r: r.company_id == self.config_id.company_id
                    )
                ],
                "qty": qty,
            }
        ]

    def _get_manual_order_payment_data(self, order, payment_method):
        return {
            "amount": order.amount_total,
            "payment_method_id": payment_method.id,
            "session_id": self.id,
            "pos_order_id": order.id,
        }

    def _add_manual_order(
        self,
        product,
        qty,
        price,
        discount,
        partner,
        fiscal_position,
        payment_method,
    ):
        self.ensure_one()
        if self.state in [
            "new_session",
            "opening_control",
            "closing_control",
            "closed",
        ]:
            raise ValidationError(
                _("Manual Order can only be added on in progress sessions")
            )
        vals = self._get_manual_order_vals(
            product, qty, price, discount, partner, fiscal_position
        )
        order_object = self.env["pos.order"].new(vals)
        order_object._onchange_amount_all()
        order = self.env["pos.order"].create(
            order_object._convert_to_write(order_object._cache)
        )
        for line_vals in self._get_manual_order_line_vals(
            product, qty, price, discount, order
        ):
            line = self.env["pos.order.line"].new(line_vals)
            line._onchange_qty()
            self.env["pos.order.line"].create(line._convert_to_write(line._cache))
            order._onchange_amount_all()

        data = self._get_manual_order_payment_data(order, payment_method)
        order.with_company(order.company_id.id).add_payment(data)
        if order._is_pos_order_paid():
            order.action_pos_order_paid()
