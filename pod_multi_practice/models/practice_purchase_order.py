# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons.purchase.models.purchase_order import PurchaseOrder as Purchase
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    """inherited purchase order"""

    _inherit = "purchase.order"

    # Define READONLY_STATES locally if it is not inherited from the parent
    READONLY_STATES = {
        "purchase": [("readonly", True)],
        "done": [("readonly", True)],
        "cancel": [("readonly", True)],
    }

    practice_id = fields.Many2one(
        "res.practice",
        string="Practice",
        store=True,
        readonly=False,
        compute="_compute_practice",
    )

    @api.depends("company_id")
    def _compute_practice(self):
        for order in self:
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

    @api.model
    def _get_picking_type(self, company_id):
        """method to set default picking type"""
        if len(self.env.user.practice_ids) == 1:
            picking_type = self.env["stock.picking.type"].search(
                [
                    ("code", "=", "incoming"),
                    ("warehouse_id.practice_id", "=", company_id),
                ]
            )
            if not picking_type:
                picking_type = self.env["stock.picking.type"].search(
                    [
                        ("code", "=", "incoming"),
                        ("warehouse_id.practice_id", "=", False),
                    ]
                )
            if not picking_type:
                error_msg = _(
                    "No warehouse could be found in the '%s' practice",
                    self.env.user.practice_id.name,
                )
                raise UserError(error_msg)
            return picking_type[:1]
        else:
            res = super(PurchaseOrder, self)._get_picking_type(company_id)
            return res

    @api.model
    def _default_picking_type(self):
        """method to get default picking type"""
        if len(self.env.user.practice_ids) == 1:
            practice = self.env.user.practice_id
            if practice:
                return self._get_picking_type(practice.id)
        else:
            return self._get_picking_type(
                self.env.context.get("company_id") or self.env.company.id
            )

    picking_type_id = fields.Many2one(
        "stock.picking.type",
        "Deliver To",
        states=READONLY_STATES,
        required=True,
        default=_default_picking_type,
        domain="['|', ('warehouse_id', '=', False), "
        "('warehouse_id.company_id', '=', company_id), "
        "'|', ('warehouse_id.practice_id', '=', practice_id), "
        "('warehouse_id.practice_id', '=', False)]",
        help="This will determine operation type of incoming shipment",
    )

    allowed_practice_ids = fields.Many2many(
        "res.practice",
        store=True,
        string="Allowed Practices",
        compute="_compute_allowed_practice_ids",
    )

    @api.depends("company_id")
    def _compute_allowed_practice_ids(self):
        for po in self:
            po.allowed_practice_ids = self.env.user.practice_ids.ids

    # @api.constrains("practice_id", "partner_id")
    # def _check_partner_practice_id(self):
    #     """method to check practice of partner and purchase order"""
    #     for order in self:
    #         practice = order.partner_id.practice_id
    #         if practice and practice != order.practice_id:
    #             raise ValidationError(
    #                 _(
    #                     "Your quotation vendor is from %(partner_practice)s "
    #                     "practice whereas your quotation belongs to %(quote_practice)s"
    #                     " practice \n Please change the "
    #                     "practice of your quotation or remove the vendor from "
    #                     "other practice.",
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
        """method to check practice of products and purchase order"""
        for order in self:
            practices = order.order_line.product_id.practice_id
            if practices and practices != order.practice_id:
                bad_products = order.order_line.product_id.filtered(
                    lambda p: p.practice_id and p.practice_id != order.practice_id
                )
                raise ValidationError(
                    _(
                        "Your quotation contains products from %(product_practice)s "
                        "practice whereas your quotation belongs to %(quote_practice)s"
                        " practice \n Please change the "
                        "practice of your quotation or remove the products from "
                        "other practices (%(bad_products)s).",
                        product_practice=", ".join(practices.mapped("name")),
                        quote_practice=order.practice_id.name,
                        bad_products=", ".join(bad_products.mapped("display_name")),
                    )
                )

    def _prepare_invoice(self):
        """override prepare_invoice function to include practice"""
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        practice_id = self.practice_id.id
        domain = [
            ("practice_id", "=", practice_id),
            ("type", "=", "purchase"),
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
                ("type", "=", "purchase"),
                ("practice_id", "=", False),
                ("company_id", "=", self.company_id.id),
            ]
            journal = self.env["account.journal"].search(domain, limit=1)
        if not journal:
            error_msg = _(
                "No journal could be found in the'%s' practice"
                " for any of those types: purchase",
                self.practice_id.name,
            )
            raise UserError(error_msg)
        invoice_vals["practice_id"] = self.practice_id.id or False
        invoice_vals["journal_id"] = journal.id
        return invoice_vals

    @api.onchange("practice_id")
    def onchange_practice_id(self):
        """onchange function"""
        if (
            self.practice_id
            and self.practice_id not in self.env.user.practice_ids
            and self.env.user.practice_ids
        ):
            raise UserError("Unauthorised Practice")
        self.picking_type_id = False
        if self.practice_id:
            picking_type = (
                self.env["stock.picking.type"]
                .sudo()
                .search(
                    [
                        ("practice_id", "=", self.practice_id.id),
                        ("company_id", "=", self.company_id.id),
                    ],
                    limit=1,
                )
            )
            self.picking_type_id = picking_type
            if not picking_type:
                picking_type = (
                    self.env["stock.picking.type"]
                    .sudo()
                    .search(
                        [
                            ("practice_id", "=", False),
                            ("company_id", "=", self.company_id.id),
                        ],
                        limit=1,
                    )
                )
            self.picking_type_id = picking_type
            if not picking_type:
                error_msg = _(
                    "No warehouse could be found in the '%s' practice",
                    self.practice_id.name,
                )
                raise UserError(error_msg)
        else:
            self.picking_type_id = (
                self.env["stock.picking.type"]
                .sudo()
                .search(
                    [
                        ("practice_id", "=", False),
                        ("company_id", "=", self.company_id.id),
                    ],
                    limit=1,
                )
            )


class PurchaseOrderLine(models.Model):
    """inherited purchase order line"""

    _inherit = "purchase.order.line"

    practice_id = fields.Many2one(
        related="order_id.practice_id", string="Practice", store=True
    )
