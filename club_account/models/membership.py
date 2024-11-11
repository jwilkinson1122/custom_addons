# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Membership(models.Model):
    _inherit = "membership"

    invoice_line_id = fields.Many2one(
        "account.move.line",
        string="Invoice Line",
        ondelete="set null",
        inverse="_inverse_invoice_line_id",
    )
    invoice_id = fields.Many2one(
        "account.move",
        related="invoice_line_id.move_id",
        string="Invoice",
        context={"short_membership_name": True},
    )
    payment_state = fields.Selection(related="invoice_line_id.move_id.payment_state")
    move_type = fields.Selection(related="invoice_line_id.move_id.move_type")
    price_paid = fields.Monetary(
        readonly=True, compute="_compute_price_paid", store=True
    )
    price_due = fields.Monetary(
        compute="_compute_price_due", inverse="_inverse_price_due", readonly=False
    )
    invoice_other_membership_ids = fields.Many2many(
        "membership", compute="_compute_invoice_other_membership_ids"
    )

    def name_get(self):
        if self._context.get("short_membership_name"):
            return [(rec.id, rec.member_id.name) for rec in self]
        return super(Membership, self).name_get()

    @api.model
    def create(self, vals):
        res = super(Membership, self).create(vals)
        res.update_invoicing()
        return res

    def write(self, vals):
        res = super(Membership, self).write(vals)
        if "state" in vals:
            self.update_invoicing()
        return res

    def unlink(self):
        self.mapped("invoice_line_id").remove_memberships(self)
        return super(Membership, self).unlink()

    @api.depends("payment_state")
    def _compute_price_paid(self):
        for rec in self:
            if rec.payment_state in ("in_payment", "paid"):
                if rec.price_due != rec.invoice_line_id.price_unit:
                    raise ValidationError(
                        _(
                            "Membership due price does is not equal to invoice unit price."
                        )
                    )
                rec.price_paid = rec.price_due

    @api.depends("invoice_line_id.price_unit")
    def _compute_price_due(self):
        for rec in self:
            if rec.invoice_line_id:
                rec.price_due = rec.invoice_line_id.price_unit

    def _inverse_price_due(self):
        for rec in self:
            if not rec.invoice_line_id:
                continue
            if rec.invoice_other_membership_ids:
                raise ValidationError(
                    _(
                        "You cannot change the due price because other memberships are linked to the same invoice.\nPlease set the status back to 'Unknown' in order to be able to change the price."
                    )
                )
            raise ValidationError(
                _(
                    "You cannot change the due price because an invoice is already attached to this membership.\nPlease change the price on the invoice line instead."
                )
            )

    @api.depends("invoice_id")
    def _compute_invoice_other_membership_ids(self):
        Membership = self.env["membership"]
        for rec in self:
            if not rec.id or not rec.invoice_id:
                rec.invoice_other_membership_ids = False
                continue
            rec.invoice_other_membership_ids = Membership.search(
                [("invoice_id", "=", rec.invoice_id.id), ("id", "!=", rec.id)],
            )

    def update_invoicing(self):
        Move = self.env["account.move"]
        MoveLine = self.env["account.move.line"]

        for rec in self:
            if rec.state not in ("requested", "member"):
                rec.invoice_line_id.remove_memberships(rec)
                continue

            if rec.invoice_line_id:
                continue

            partner = rec.contact_person_id or rec.member_id
            invoices = Move.search(
                [("state", "=", "draft"), ("partner_id", "=", partner.id)]
            )

            inv_lines = invoices.mapped("line_ids").filtered(
                lambda invl: invl.product_id == rec.period_category_id.product_id
                and invl.price_unit == rec.price_due
            )

            if inv_lines:
                rec.invoice_line_id = inv_lines[0]
                continue

            inv_lines = invoices.mapped("line_ids").filtered(
                lambda invl: invl.product_id.product_tmpl_id
                == rec.period_id.product_tmpl_id
            )

            if inv_lines:
                invoice = inv_lines[0].move_id
            elif invoices:
                invoice = invoices[0]
            else:
                invoice = Move.create(
                    {
                        "move_type": "out_invoice",
                        "partner_id": partner.id,
                    }
                )

            move_line_vals = {
                "move_id": invoice.id,
                "product_id": rec.period_category_id.product_id.id,
                "membership_ids": [(4, rec.id)],
                "price_unit": rec.price_due,
            }

            # Set additional fields that would have been set by `_onchange_product_id`
            product = rec.period_category_id.product_id
            if product:
                move_line_vals.update(
                    {
                        "name": product.name,
                        "account_id": product.property_account_income_id.id
                        or product.categ_id.property_account_income_categ_id.id,
                        "quantity": 1,
                    }
                )

            MoveLine.create(move_line_vals)

    def _inverse_invoice_line_id(self):
        self.mapped("invoice_line_id")._inverse_membership_ids()

    def validate_membership_payment(self):
        self.ensure_one()
        if not self.invoice_id:
            self.update_invoicing()
        invoice = self.invoice_id
        if (
            invoice.state == "draft"
            and not invoice.auto_post
            and invoice.move_type != "entry"
        ):
            invoice.action_post()
        if (
            invoice.state == "posted"
            and invoice.payment_state in ("not_paid", "partial")
            and invoice.move_type
            in (
                "out_invoice",
                "out_refund",
                "in_invoice",
                "in_refund",
                "out_receipt",
                "in_receipt",
            )
        ):
            action = invoice.action_register_payment()
            action["context"]["dont_redirect_to_payments"] = True
            return action
        elif invoice.state == "posted" and invoice.payment_state == "paid":
            return True
        raise ValidationError(
            _(
                "The invoice '%s' has been posted but it seems you cannot register a payment.\nPlease contact your administrator."
            )
            % invoice.name_get()[0][1]
        )
