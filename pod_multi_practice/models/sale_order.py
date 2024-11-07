# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    """inherited sale order"""

    _inherit = "sale.order"

    @api.model
    def _default_warehouse_id(self):
        """method to get default warehouse id"""
        # !!! Any change to the default value may have to be repercuted
        # on _init_column() below.
        return self.env.user._get_default_warehouse_id()

    practice_id = fields.Many2one(
        "res.practice",
        string="Practice",
        store=True,
        readonly=False,
        compute="_compute_practice",
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        required=True,
        compute="_compute_warehouse_id",
        store=True,
        readonly=False,
        precompute=True,
        states={
            "sale": [("readonly", True)],
            "done": [("readonly", False)],
            "cancel": [("readonly", False)],
        },
        check_company=True,
    )
    allowed_practice_ids = fields.Many2many(
        "res.practice",
        store=True,
        string="Allowed Practices",
        compute="_compute_allowed_practice_ids",
    )

    @api.depends("company_id")
    def _compute_allowed_practice_ids(self):
        for so in self:
            so.allowed_practice_ids = self.env.user.practice_ids.ids

    @api.depends("company_id")
    def _compute_practice(self):
        for order in self:
            order.practice_id = False
            if len(self.env.user.practice_ids) == 1:
                company = self.env.company
                so_company = order.company_id if order.company_id else self.env.company
                practice_ids = self.env.user.practice_ids
                practice = practice_ids.filtered(
                    lambda practice: practice.company_id == so_company
                )
                if practice:
                    order.practice_id = practice.ids[0]
                else:
                    order.practice_id = False

    # @api.constrains("practice_id", "partner_id")
    # def _check_partner_practice_id(self):
    #     """method to check practice of partner and sale order"""
    #     for order in self:
    #         practice = order.partner_id.practice_id
    #         if practice and practice != order.practice_id:
    #             raise ValidationError(
    #                 _(
    #                     "Your quotation customer have company practice "
    #                     "%(partner_practice)s whereas your quotation belongs to "
    #                     "company practice %(quote_practice)s. \n Please change the "
    #                     "company of your quotation or change the customer from "
    #                     "other practice",
    #                     partner_practice=practice.name,
    #                     quote_practice=order.practice_id.name,
    #                 )
    #             )

    @api.constrains("practice_id", "partner_id")
    def _check_partner_practice_id(self):
        """method to check practices of partner and sale order"""
        for order in self:
            if (
                order.partner_id
                and order.practice_id not in order.partner_id.practice_ids
            ):
                raise ValidationError(
                    _(
                        "The selected partner is not associated with the selected practice."
                    )
                )

    @api.constrains("practice_id", "order_line")
    def _check_order_line_practice_id(self):
        """method to check practice of products and sale order"""
        for order in self:
            practices = order.order_line.product_id.practice_id
            if practices and practices != order.practice_id:
                bad_products = order.order_line.product_id.filtered(
                    lambda p: p.practice_id and p.practice_id != order.practice_id
                )
                raise ValidationError(
                    _(
                        "Your quotation contains products from company practice "
                        "%(product_practice)s whereas your quotation belongs to "
                        "company practice %(quote_practice)s. \n Please change the "
                        "company of your quotation or remove the products from "
                        "other companies (%(bad_products)s).",
                        product_practice=", ".join(practices.mapped("name")),
                        quote_practice=order.practice_id.name,
                        bad_products=", ".join(bad_products.mapped("display_name")),
                    )
                )

    def _prepare_invoice(self):
        """override prepare_invoice function to include practice"""
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        practice_id = self.practice_id.id
        domain = [
            ("practice_id", "=", practice_id),
            ("type", "=", "sale"),
            ("code", "!=", "POSS"),
            ("company_id", "=", self.company_id.id),
        ]

        journal = None
        if self._context.get("default_currency_id"):
            currency_domain = domain + [
                ("currency_id", "=", self._context["default_currency_id"])
            ]
            journal = self.env["account.journal"].search(currency_domain, limit=1)

        if not journal:
            journal = self.env["account.journal"].search(domain, limit=1)
        if not journal:
            domain = [
                ("type", "=", "sale"),
                ("code", "!=", "POSS"),
                ("practice_id", "=", False),
                ("company_id", "=", self.company_id.id),
            ]
            journal = self.env["account.journal"].search(domain, limit=1)
        if not journal:
            error_msg = _(
                "No journal could be found in the '%s' practice"
                " for any of those types: sale",
                self.practice_id.name,
            )
            raise UserError(error_msg)

        invoice_vals["practice_id"] = self.practice_id.id or False
        invoice_vals["journal_id"] = journal.id
        return invoice_vals

    @api.onchange("practice_id")
    def onchange_practice_id(self):
        """onchange method"""

        if (
            self.practice_id
            and self.practice_id not in self.env.user.practice_ids
            and self.env.user.practice_ids
        ):
            raise UserError("Unauthorised Practice")
        self.warehouse_id = False
        if self.practice_id:
            warehouse = (
                self.env["stock.warehouse"]
                .sudo()
                .search(
                    [
                        ("practice_id", "=", self.practice_id.id),
                        ("company_id", "=", self.company_id.id),
                    ],
                    limit=1,
                )
            )
            self.warehouse_id = warehouse
            if not warehouse:

                warehouse = (
                    self.env["stock.warehouse"]
                    .sudo()
                    .search(
                        [
                            ("practice_id", "=", False),
                            ("company_id", "=", self.company_id.id),
                        ],
                        limit=1,
                    )
                )
                self.warehouse_id = warehouse
            if not warehouse:
                error_msg = _(
                    "No warehouse could be found in the '%s' practice",
                    self.practice_id.name,
                )
                raise UserError(error_msg)
        else:

            self.warehouse_id = (
                self.env["stock.warehouse"]
                .sudo()
                .search(
                    [
                        ("practice_id", "=", False),
                        ("company_id", "=", self.company_id.id),
                    ],
                    limit=1,
                )
            )


class SaleOrderLine(models.Model):
    """inherited purchase order line"""

    _inherit = "sale.order.line"

    practice_id = fields.Many2one(
        related="order_id.practice_id", string="Practice", store=True
    )
