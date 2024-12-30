from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class WizardSectionConfiguration(models.Model):
    _name = "wizard.section.configuration"
    _description = "Wizard Section Configuration"

    section_name = fields.Selection(
        [
            ("start", "Start"),
            ("configure", "Configure"),
            ("custom", "Customize"),
            ("summary", "Summary"),
            ("final", "Final"),
        ],
        string="Section",
        required=True,
    )
    product_category_id = fields.Many2one(
        "product.category",
        string="Product Category",
        required=True,
        help="The product category to display in this wizard section.",
    )

    _sql_constraints = [
        (
            "unique_section_name",
            "unique(section_name)",
            "Each section can only be linked to one product category.",
        ),
    ]


class SaleOrderWizard(models.TransientModel):
    _name = "sale.order.wizard"
    _inherit = ["multi.step.wizard.mixin"]

    # General fields
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
        domain=lambda self: self._get_product_domain(),
        required=True,
    )

    # Section-specific fields
    start_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Start Product",
        domain=lambda self: self._get_product_domain("start"),
    )

    start_selected_attribute_value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        relation="sale_order_wizard_start_attribute_rel",  # Unique table name
        column1="wizard_id",  # Column for the wizard ID
        column2="attribute_id",  # Column for the attribute ID
        string="Start Selected Attributes",
    )

    configure_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Configure Product",
        domain=lambda self: self._get_product_domain("configure"),
    )

    selected_attribute_value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        string="Selected Attributes",
        help="Selected attribute values for the product",
    )

    configure_selected_attribute_value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        relation="sale_order_wizard_configure_attribute_rel",  # Unique table name
        column1="wizard_id",
        column2="attribute_id",
        string="Configure Selected Attributes",
    )

    available_attribute_values = fields.Many2many(
        comodel_name="product.attribute.value",
        compute="_compute_available_attribute_values",
        string="Available Attribute Values",
    )

    # Add a field to dynamically fetch the category
    current_category_id = fields.Many2one(
        "product.category",
        string="Current Product Category",
        compute="_compute_current_category",
    )

    @api.depends("state")
    def _compute_current_category(self):
        """Fetch the product category based on the current section."""
        for wizard in self:
            configuration = self.env["wizard.section.configuration"].search(
                [("section_name", "=", wizard.state)], limit=1
            )
            wizard.current_category_id = (
                configuration.product_category_id if configuration else None
            )

    def _get_product_domain(self, section):
        """Get domain for a specific section."""
        configuration = self.env["wizard.section.configuration"].search(
            [("section_name", "=", section)], limit=1
        )
        if configuration and configuration.product_category_id:
            return [
                ("categ_id", "child_of", configuration.product_category_id.id),
                ("sale_ok", "=", True),
            ]
        return [("sale_ok", "=", True)]

    @api.onchange("state")
    def _onchange_state(self):
        """Set the correct product domain based on the current section."""
        domain = self._get_product_domain(self.state)
        if self.state == "start":
            self.start_product_id = None
        elif self.state == "configure":
            self.configure_product_id = None
        return {"domain": {"product_id": domain}}

    @api.onchange("product_id")
    def _onchange_product_id(self):
        """Reset selected attributes and recompute available values."""
        if self.product_id:
            self.selected_attribute_value_ids = [(5, 0, 0)]
        self._compute_available_attribute_values()

    product_variant_id = fields.Many2one(
        comodel_name="product.product",
        string="Product Variant",
        compute="_compute_product_variant",
        store=True,
    )

    field1 = fields.Char(string="Configuration 1")
    field2 = fields.Char(string="Configuration 2")
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

    @api.depends("product_id")
    def _compute_available_attribute_values(self):
        """Compute the available attribute values for the selected product."""
        for wizard in self:
            if wizard.product_id:
                wizard.available_attribute_values = (
                    wizard.product_id.product_tmpl_id.attribute_line_ids.mapped(
                        "value_ids"
                    )
                )
            else:
                wizard.available_attribute_values = self.env["product.attribute.value"]

    @api.depends(
        "product_id", "selected_attribute_value_ids", "field1", "field2", "field3"
    )
    def _compute_summary(self):
        """Generate a summary of the selected configurations."""
        for wizard in self:
            summary_lines = []
            if wizard.product_id:
                summary_lines.append(f"Product: {wizard.product_id.name}")

            if wizard.selected_attribute_value_ids:
                attributes = ", ".join(
                    wizard.selected_attribute_value_ids.mapped("name")
                )
                summary_lines.append(f"Attributes: {attributes}")

            if wizard.field1:
                summary_lines.append(f"Configuration 1: {wizard.field1}")
            if wizard.field2:
                summary_lines.append(f"Configuration 2: {wizard.field2}")
            if wizard.field3:
                summary_lines.append(f"Customization: {wizard.field3}")

            wizard.summary = "\n".join(summary_lines)

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

    # Ensure state-specific validation
    def state_exit_start(self):
        """Transition from Start section."""
        if not self.start_product_id:
            raise ValidationError(_("Please select a product in the Start section."))
        self.state = "configure"

    # def state_exit_start(self):
    #     """Move to the configure state."""
    #     if not self.product_id:
    #         raise ValidationError(
    #             _("Please select a product before proceeding in the Start section.")
    #         )
    #     if not self.field1:
    #         raise ValidationError(
    #             _("Configuration 1 is required in the Start section.")
    #         )
    #     self.selected_attribute_value_ids = [(5, 0, 0)]
    #     self.state = "configure"

    def state_exit_configure(self):
        """Transition from Configure section."""
        if not self.configure_product_id:
            raise ValidationError(
                _("Please select a product in the Configure section.")
            )
        self.state = "custom"

    # def state_exit_configure(self):
    #     """Move to the custom state."""
    #     if not self.product_id:
    #         raise ValidationError(
    #             _("Please select a product before proceeding in the Configure section.")
    #         )
    #     if not self.selected_attribute_value_ids:
    #         raise ValidationError(
    #             _(
    #                 "Please select at least one attribute value in the Configure section."
    #             )
    #         )
    #     if not self.field2:
    #         raise ValidationError(
    #             _("Configuration 2 is required in the Configure section.")
    #         )
    #     self.state = "custom"

    def state_exit_custom(self):
        """Move to the summary state."""
        self.field3 = None  # Optional: Reset customization field if needed
        self.state = "summary"

    def state_exit_final(self):
        """Save wizard selections to the sales order line."""
        if not self.sale_order_id:
            raise ValidationError(_("No associated sale order found."))

        description = f"{self.product_id.name or 'Product'}"
        if self.selected_attribute_value_ids:
            attributes = ", ".join(self.selected_attribute_value_ids.mapped("name"))
            description += f" - {attributes}"

        if self.field1:
            description += f" | Config1: {self.field1}"
        if self.field2:
            description += f" | Config2: {self.field2}"
        if self.field3:
            description += f" | Custom: {self.field3}"

        self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order_id.id,
                "product_id": self.product_id.id,
                "product_uom_qty": 1,
                "price_unit": self.computed_price,
                "name": description,
            }
        )

    @api.model
    def create(self, vals):
        """Ensure product_id is set when the wizard is created."""
        wizard = super().create(vals)
        if not wizard.product_id:
            domain = wizard._get_product_domain()
            default_product = wizard.env["product.product"].search(domain, limit=1)
            if default_product:
                wizard.product_id = default_product
            else:
                raise ValidationError(
                    _("No products available for the selected category.")
                )
        return wizard
