from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SaleOrderWizard(models.TransientModel):
    _name = "sale.order.wizard"
    _inherit = ["multi.step.wizard.mixin"]

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sales Order",
        required=True,
        ondelete="cascade",
        default=lambda self: self._default_sale_order_id(),
    )

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Select Product",
        domain=[("sale_ok", "=", True)],
        required=True,
        default=lambda self: self._default_product_id(),
    )

    @api.model
    def _default_product_id(self):
        product = self.env["product.product"].search([("sale_ok", "=", True)], limit=1)
        if not product:
            raise ValidationError(_("No saleable product found in the system."))
        return product.id

    product_variant_id = fields.Many2one(
        comodel_name="product.product",
        string="Product Variant",
        compute="_compute_product_variant",
        store=True,
    )

    field1 = fields.Char(string="Configuration 1", required=True)
    field2 = fields.Char(string="Configuration 2", required=True)
    field3 = fields.Char(string="Customization")

    computed_price = fields.Float(
        string="Computed Price",
        compute="_compute_price",
        store=True,
    )

    @api.depends("field1", "field2", "field3")
    def _compute_price(self):
        for wizard in self:
            base_price = 100.0
            extra_field1 = 10.0 if wizard.field1 else 0.0
            extra_field2 = 20.0 if wizard.field2 else 0.0
            extra_custom = 30.0 if wizard.field3 else 0.0
            wizard.computed_price = (
                base_price + extra_field1 + extra_field2 + extra_custom
            )

    summary_label = fields.Char(
        "Selection Summary Label",
        translate=True,
        default="Summary of Selections:",
        readonly=True,
    )

    summary = fields.Text(string="Summary", compute="_compute_summary")

    @api.depends("product_id", "field1", "field2", "field3")
    def _compute_summary(self):
        for wizard in self:
            product_name = wizard.product_id.name or "No product selected"
            config1 = wizard.field1 or "N/A"
            config2 = wizard.field2 or "N/A"
            customization = wizard.field3 or "N/A"
            wizard.summary = (
                f"Product: {product_name}\n"
                f"Configuration 1: {config1}\n"
                f"Configuration 2: {config2}\n"
                f"Customization: {customization}"
            )

    @api.model
    def _selection_state(self):
        return [
            ("start", "Start"),
            ("configure", "Configure"),
            ("custom", "Customize"),
            ("summary", "Summary"),
            ("final", "Final"),
        ]

    @api.model
    def _default_sale_order_id(self):
        return self.env.context.get("active_id")

    def state_exit_start(self):
        self.state = "configure"

    def state_exit_configure(self):
        if not self.product_id:
            raise ValidationError(_("Please select a product before proceeding."))
        if not self.field1 or not self.field2:
            raise ValidationError(_("Configuration fields cannot be empty."))
        self.state = "custom"

    def state_exit_custom(self):
        self.state = "summary"

    def state_exit_final(self):
        """Save wizard selections to the sales order line."""
        if self.sale_order_id:
            product_id = (
                self.product_variant_id.id
                if self.product_variant_id
                else self.product_id.id
            )
            name = (
                f"Customized {self.product_variant_id.name}"
                if self.product_variant_id
                else f"{self.product_id.name}: Config1={self.field1}, Config2={self.field2}, Custom={self.field3}"
            )
            order_line_values = {
                "order_id": self.sale_order_id.id,
                "product_id": product_id,
                "product_uom_qty": 1,
                "price_unit": self.computed_price,
                "name": name,
            }
            self.env["sale.order.line"].create(order_line_values)
