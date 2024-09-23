# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo.tools.misc import format_date

class PrescriptionOrderLine(models.Model):
    _name = "prescription.order.line"
    _description = "Prescription Order Line"
    _inherit = ["mail.thread", "mail.activity.mixin", "analytic.mixin"]

    @api.depends(
        "original_uom_qty",
        "price_unit",
        "taxes_id",
        "order_id.partner_id",
        "product_id",
        "currency_id",
    )
    def _compute_amount(self):
        for line in self:
            price = line.price_unit
            taxes = line.taxes_id.compute_all(
                price,
                line.currency_id,
                line.original_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_id,
            )
            line.update(
                {
                    "price_tax": sum(
                        t.get("amount", 0.0) for t in taxes.get("taxes", [])
                    ),
                    "price_total": taxes["total_included"],
                    "price_subtotal": taxes["total_excluded"],
                }
            )

    name = fields.Char("Description", tracking=True)
    sequence = fields.Integer()
    order_id = fields.Many2one("prescription.order", required=True, ondelete="cascade")
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        domain=[("sale_ok", "=", True)],
    )
    product_uom = fields.Many2one("uom.uom", string="Unit of Measure")
    price_unit = fields.Float(string="Price", digits="Product Price")
    taxes_id = fields.Many2many(
        "account.tax",
        string="Taxes",
        domain=["|", ("active", "=", False), ("active", "=", True)],
    )
    date_schedule = fields.Date(string="Scheduled Date")
    original_uom_qty = fields.Float(
        string="Original quantity", default=1, digits="Product Unit of Measure"
    )
    ordered_uom_qty = fields.Float(
        string="Ordered quantity", compute="_compute_quantities", store=True
    )
    invoiced_uom_qty = fields.Float(
        string="Invoiced quantity", compute="_compute_quantities", store=True
    )
    remaining_uom_qty = fields.Float(
        string="Remaining quantity", compute="_compute_quantities", store=True
    )
    remaining_qty = fields.Float(
        string="Remaining quantity in base UoM",
        compute="_compute_quantities",
        store=True,
    )
    delivered_uom_qty = fields.Float(
        string="Delivered quantity", compute="_compute_quantities", store=True
    )
    sale_lines = fields.One2many(
        "sale.order.line",
        "prescription_order_line",
        string="Sale order lines",
        readonly=True,
        copy=False,
    )
    company_id = fields.Many2one(
        related="order_id.company_id", store=True, index=True, precompute=True
    )
    currency_id = fields.Many2one("res.currency", related="order_id.currency_id")
    partner_id = fields.Many2one(related="order_id.partner_id", string="Customer")
    user_id = fields.Many2one(related="order_id.user_id", string="Responsible")
    payment_term_id = fields.Many2one(
        related="order_id.payment_term_id", string="Payment Terms"
    )
    pricelist_id = fields.Many2one(related="order_id.pricelist_id", string="Pricelist")
    price_subtotal = fields.Monetary(
        compute="_compute_amount", string="Subtotal", store=True
    )
    price_total = fields.Monetary(compute="_compute_amount", string="Total", store=True)
    price_tax = fields.Float(compute="_compute_amount", string="Tax", store=True)
    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")],
        default=False,
        help="Technical field for UX purpose.",
    )
    pricelist_item_id = fields.Many2one(
        comodel_name="product.pricelist.item", compute="_compute_pricelist_item_id"
    )

    # custom_value_ids = fields.One2many(
    #     comodel_name="product.config.session.custom.value",
    #     inverse_name="cfg_session_id",
    #     related="config_session_id.custom_value_ids",
    #     string="Configurator Custom Values",
    # )
    # config_ok = fields.Boolean(
    #     related="product_id.config_ok", string="Configurable", readonly=True
    # )
    # config_session_id = fields.Many2one(
    #     comodel_name="product.config.session", string="Config Session"
    # )
    # state = fields.Selection(related="order_id.state")

    # def reconfigure_product(self):
    #     """Creates and launches a product configurator wizard with a linked
    #     template and variant in order to re-configure a existing product. It is
    #     esetially a shortcut to pre-fill configuration data of a variant"""
    #     wizard_model = "product.configurator.prescription.order"

    #     extra_vals = {
    #         "order_id": self.order_id.id,
    #         "order_line_id": self.id,
    #         "product_id": self.product_id.id,
    #     }
    #     self = self.with_context(
    #         default_order_id=self.order_id.id,
    #         default_order_line_id=self.id,
    #     )
    #     return self.product_id.product_tmpl_id.create_config_wizard(
    #         model_name=wizard_model, extra_vals=extra_vals
    #     )

    # @api.depends("product_id")
    # def _compute_name(self):
    #     for line in self:
    #         name = ""
    #         custom_values = line.custom_value_ids
    #         if custom_values:
    #             name += "\n" + "\n".join(
    #                 [f"{cv.display_name}: {cv.value}" for cv in custom_values]
    #             )
    #         else:
    #             if not line.product_id:
    #                 continue
    #             name = self.product_id.get_product_multiline_description_sale()
    #         line.name = name


    @api.depends(
        "order_id.name", "date_schedule", "remaining_uom_qty", "product_uom.name"
    )
    @api.depends_context("from_sale_order")
    def _compute_display_name(self):
        if self.env.context.get("from_sale_order"):
            for record in self:
                name = "[%s]" % record.order_id.name
                if record.date_schedule:
                    formatted_date = format_date(record.env, record.date_schedule)
                    name += " - {}: {}".format(_("Date Scheduled"), formatted_date)
                name += " ({}: {} {})".format(
                    _("remaining"),
                    record.remaining_uom_qty,
                    record.product_uom.name,
                )
                record.display_name = name
        else:
            return super()._compute_display_name()

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        """Retrieve the price before applying the pricelist
        :param obj product: object of current product record
        :param float qty: total quentity of product
        :param tuple price_and_rule: tuple(price, suitable_rule) coming
               from pricelist computation
        :param obj uom: unit of measure of current order line
        :param integer pricelist_id: pricelist id of sale order"""
        # Copied and adapted from the sale module
        PricelistItem = self.env["product.pricelist.item"]
        field_name = "lst_price"
        currency_id = None
        product_currency = None
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == "without_discount":
                while (
                    pricelist_item.base == "pricelist"
                    and pricelist_item.base_pricelist_id
                    and pricelist_item.base_pricelist_id.discount_policy
                    == "without_discount"
                ):
                    price, rule_id = pricelist_item.base_pricelist_id.with_context(
                        uom=uom.id
                    )._get_product_price_rule(product, qty, uom)
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == "standard_price":
                field_name = "standard_price"
            if pricelist_item.base == "pricelist" and pricelist_item.base_pricelist_id:
                field_name = "price"
                product = product.with_context(
                    pricelist=pricelist_item.base_pricelist_id.id
                )
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        product_currency = (
            product_currency
            or (product.company_id and product.company_id.currency_id)
            or self.env.company.currency_id
        )
        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(
                    product_currency, currency_id
                )

        product_uom = product.uom_id.id
        if uom and uom.id != product_uom:
            # the unit price is in a different uom
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id.id

    def _get_display_price(self):
        # Copied and adapted from the sale module
        self.ensure_one()
        self.product_id.ensure_one()

        pricelist_price = self.pricelist_item_id._compute_price(
            product=self.product_id,
            quantity=self.original_uom_qty or 1.0,
            uom=self.product_uom,
            date=fields.Date.today(),
            currency=self.currency_id,
        )

        if self.order_id.pricelist_id.discount_policy == "with_discount":
            return pricelist_price

        if not self.pricelist_item_id:
            # No pricelist rule found => no discount from pricelist
            return pricelist_price

        base_price = self._get_pricelist_price_before_discount()

        # negative discounts (= surcharge) are included in the display price
        return max(base_price, pricelist_price)

    def _get_pricelist_price_before_discount(self):
        # Copied and adapted from the sale module
        self.ensure_one()
        self.product_id.ensure_one()

        return self.pricelist_item_id._compute_price_before_discount(
            product=self.product_id,
            quantity=self.product_uom_qty or 1.0,
            uom=self.product_uom,
            date=fields.Date.today(),
            currency=self.currency_id,
        )

    @api.onchange("product_id", "original_uom_qty")
    def onchange_product(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        if self.product_id:
            name = self.product_id.name
            if not self.product_uom:
                self.product_uom = self.product_id.uom_id.id
            if self.order_id.partner_id and float_is_zero(
                self.price_unit, precision_digits=precision
            ):
                self.price_unit = self._get_display_price()
            if self.product_id.code:
                name = f"[{name}] {self.product_id.code}"
            if self.product_id.description_sale:
                name += "\n" + self.product_id.description_sale
            self.name = name

            fpos = self.order_id.fiscal_position_id
            if self.env.uid == SUPERUSER_ID:
                company_id = self.env.company.id
                self.taxes_id = fpos.map_tax(
                    self.product_id.taxes_id.filtered(
                        lambda r: r.company_id.id == company_id
                    )
                )
            else:
                self.taxes_id = fpos.map_tax(self.product_id.taxes_id)

    @api.depends(
        "sale_lines.order_id.state",
        "sale_lines.prescription_order_line",
        "sale_lines.product_uom_qty",
        "sale_lines.product_uom",
        "sale_lines.qty_delivered",
        "sale_lines.qty_invoiced",
        "original_uom_qty",
        "product_uom",
    )
    def _compute_quantities(self):
        for line in self:
            sale_lines = line.sale_lines
            line.ordered_uom_qty = sum(
                sl.product_uom._compute_quantity(sl.product_uom_qty, line.product_uom)
                for sl in sale_lines
                if sl.order_id.state != "cancel" and sl.product_id == line.product_id
            )
            line.invoiced_uom_qty = sum(
                sl.product_uom._compute_quantity(sl.qty_invoiced, line.product_uom)
                for sl in sale_lines
                if sl.order_id.state != "cancel" and sl.product_id == line.product_id
            )
            line.delivered_uom_qty = sum(
                sl.product_uom._compute_quantity(sl.qty_delivered, line.product_uom)
                for sl in sale_lines
                if sl.order_id.state != "cancel" and sl.product_id == line.product_id
            )
            line.remaining_uom_qty = line.original_uom_qty - line.ordered_uom_qty
            line.remaining_qty = line.product_uom._compute_quantity(
                line.remaining_uom_qty, line.product_id.uom_id
            )

    @api.depends("product_id", "product_uom", "original_uom_qty")
    def _compute_pricelist_item_id(self):
        # Copied and adapted from the sale module
        for line in self:
            if (
                not line.product_id
                or line.display_type
                or not line.order_id.pricelist_id
            ):
                line.pricelist_item_id = False
            else:
                line.pricelist_item_id = line.order_id.pricelist_id._get_product_rule(
                    line.product_id,
                    quantity=line.original_uom_qty or 1.0,
                    uom=line.product_uom,
                    date=fields.Date.today(),
                )

    def _validate(self):
        try:
            for line in self:
                assert (
                    not line.display_type and line.price_unit > 0.0
                ) or line.display_type, _("Price must be greater than zero")
                assert (
                    not line.display_type and line.original_uom_qty > 0.0
                ) or line.display_type, _("Quantity must be greater than zero")
        except AssertionError as e:
            raise UserError(e) from e

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get(
                "display_type", self.default_get(["display_type"])["display_type"]
            ):
                values.update(product_id=False, price_unit=0, product_uom=False)

        return super().create(vals_list)

    _sql_constraints = [
        (
            "accountable_required_fields",
            """
            CHECK(
                display_type IS NOT NULL OR (
                    product_id IS NOT NULL AND product_uom IS NOT NULL
                    )
            )
            """,
            "Missing required fields on accountable sale order line.",
        ),
        (
            "non_accountable_null_fields",
            """
            CHECK(
                display_type IS NULL OR (
                    product_id IS NULL AND price_unit = 0 AND product_uom IS NULL
                    )
            )
            """,
            "Forbidden values on non-accountable sale order line",
        ),
    ]

    def write(self, values):
        if "display_type" in values and self.filtered(
            lambda line: line.display_type != values.get("display_type")
        ):
            raise UserError(
                _(
                    """
                    You cannot change the type of a sale order line.
                    Instead you should delete the current line and create a new line
                    of the proper type.
                    """
                )
            )
        return super().write(values)
