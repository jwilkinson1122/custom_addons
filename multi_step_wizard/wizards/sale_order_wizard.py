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
    field1 = fields.Char(string="Configuration 1", default="N/A")
    field2 = fields.Char(string="Configuration 2", default="N/A")
    field3 = fields.Char(string="Customization", default="N/A")

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
        # required=True,
    )

    product_template_id = fields.Many2one(
        comodel_name="product.template",
        string="Product Template",
        compute="_compute_product_template",
        store=True,
    )

    # start section fields
    start_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Start Product",
        domain=lambda self: self._get_product_domain("start"),
    )

    selected_attribute_value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        string="Selected Attributes",
        help="Selected attribute values for the product",
    )

    start_selected_attribute_value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        relation="sale_order_wizard_start_attribute_rel",  # Unique table name
        column1="wizard_id",  # Column for the wizard ID
        column2="attribute_id",  # Column for the attribute ID
        string="Start Selected Attributes",
    )

    start_product_price = fields.Float(
        string="Start Product Price", compute="_compute_start_price", readonly=True
    )

    start_attribute_price = fields.Float(
        string="Start Attribute Price", compute="_compute_start_price", readonly=True
    )

    @api.depends("start_product_id", "start_selected_attribute_value_ids")
    def _compute_start_price(self):
        for wizard in self:
            wizard.start_product_price = (
                wizard.start_product_id.list_price if wizard.start_product_id else 0.0
            )
            wizard.start_attribute_price = sum(
                self.env["product.template.attribute.value"]
                .search(
                    [
                        (
                            "product_tmpl_id",
                            "=",
                            wizard.start_product_id.product_tmpl_id.id,
                        ),
                        (
                            "product_attribute_value_id",
                            "in",
                            wizard.start_selected_attribute_value_ids.ids,
                        ),
                    ]
                )
                .mapped("price_extra")
            )

    # configure section fields
    configure_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Configure Product",
        domain=lambda self: self._get_product_domain("configure"),
    )

    configure_selected_attribute_value_ids = fields.Many2many(
        comodel_name="product.attribute.value",
        relation="sale_order_wizard_configure_attribute_rel",  # Unique table name
        column1="wizard_id",
        column2="attribute_id",
        string="Configure Selected Attributes",
    )

    configure_product_price = fields.Float(
        string="Configure Product Price",
        compute="_compute_configure_price",
        readonly=True,
    )

    configure_attribute_price = fields.Float(
        string="Configure Attribute Price",
        compute="_compute_configure_price",
        readonly=True,
    )

    @api.depends("configure_product_id", "configure_selected_attribute_value_ids")
    def _compute_configure_price(self):
        for wizard in self:
            wizard.configure_product_price = (
                wizard.configure_product_id.list_price
                if wizard.configure_product_id
                else 0.0
            )
            wizard.configure_attribute_price = sum(
                self.env["product.template.attribute.value"]
                .search(
                    [
                        (
                            "product_tmpl_id",
                            "=",
                            wizard.configure_product_id.product_tmpl_id.id,
                        ),
                        (
                            "product_attribute_value_id",
                            "in",
                            wizard.configure_selected_attribute_value_ids.ids,
                        ),
                    ]
                )
                .mapped("price_extra")
            )

    available_attribute_values = fields.Many2many(
        comodel_name="product.attribute.value",
        compute="_compute_available_attribute_values",
        string="Available Attribute Values",
    )

    current_category_id = fields.Many2one(
        "product.category",
        string="Current Product Category",
        compute="_compute_current_category",
    )

    product_variant_id = fields.Many2one(
        comodel_name="product.product",
        string="Product Variant",
        compute="_compute_product_variant",
        store=True,
    )

    computed_price = fields.Float(
        string="Computed Price", compute="_compute_price", store=True, readonly=True
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    product_price = fields.Float(
        string="Product Price", compute="_compute_product_price", readonly=True
    )

    attribute_price = fields.Float(
        string="Attribute Price", compute="_compute_attribute_price", readonly=True
    )

    formatted_product_price = fields.Char(
        string="Product Price",
        compute="_compute_formatted_product_price",
        readonly=True,
    )

    formatted_attribute_price = fields.Char(
        string="Attribute Price",
        compute="_compute_formatted_attribute_price",
        readonly=True,
    )

    formatted_total_price = fields.Char(
        string="Total Price", compute="_compute_formatted_total_price", readonly=True
    )

    running_total_price = fields.Float(
        string="Running Total Price",
        compute="_compute_running_total_price",
        readonly=True,
        store=True,
    )

    summary_label = fields.Char(
        "Selection Summary Label",
        translate=True,
        default="Summary of Selections:",
        readonly=True,
    )

    summary = fields.Text(string="Summary", compute="_compute_summary", default="")

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

    @api.onchange("state")
    def _onchange_state(self):
        """Handle changes in wizard state."""
        configuration = self.env["wizard.section.configuration"].search(
            [("section_name", "=", self.state)], limit=1
        )
        self.current_category_id = (
            configuration.product_category_id if configuration else None
        )

        # Reset fields for the current state
        if self.state == "start":
            self.start_product_id = False
            self.start_selected_attribute_value_ids = [(5, 0, 0)]
            self.start_product_price = 0.0
            self.start_attribute_price = 0.0
        elif self.state == "configure":
            self.configure_product_id = False
            self.configure_selected_attribute_value_ids = [(5, 0, 0)]
            self.configure_product_price = 0.0
            self.configure_attribute_price = 0.0

    @api.onchange("product_id")
    def _onchange_product_id(self):
        """Reset selected attributes and recompute available values."""
        if self.product_id:
            self.selected_attribute_value_ids = [(5, 0, 0)]
        self._compute_available_attribute_values()

    @api.depends("start_product_id", "configure_product_id")
    def _compute_product_template(self):
        for wizard in self:
            # Prioritize start_product_id if it exists
            if wizard.start_product_id:
                wizard.product_template_id = wizard.start_product_id.product_tmpl_id
            elif wizard.configure_product_id:
                wizard.product_template_id = wizard.configure_product_id.product_tmpl_id
            else:
                wizard.product_template_id = False

    @api.depends("start_product_id")
    def _compute_product_price(self):
        for wizard in self:
            wizard.product_price = (
                wizard.start_product_id.list_price if wizard.start_product_id else 0.0
            )

    @api.depends("start_selected_attribute_value_ids", "start_product_id")
    def _compute_attribute_price(self):
        for wizard in self:
            extra_price = 0.0
            if wizard.start_product_id:
                for attribute in wizard.start_selected_attribute_value_ids:
                    template_value = self.env[
                        "product.template.attribute.value"
                    ].search(
                        [
                            (
                                "product_tmpl_id",
                                "=",
                                wizard.start_product_id.product_tmpl_id.id,
                            ),
                            ("product_attribute_value_id", "=", attribute.id),
                        ],
                        limit=1,
                    )
                    if template_value:
                        _logger.info(
                            f"Attribute {attribute.name} found with Price Extra: {template_value.price_extra}"
                        )
                        extra_price += template_value.price_extra
                    else:
                        _logger.warning(
                            f"Attribute {attribute.name} (ID: {attribute.id}) not linked to product {wizard.start_product_id.name} (ID: {wizard.start_product_id.id})"
                        )
                        # _logger.warning(
                        #     f"Attribute {attribute.name} not linked to product {wizard.start_product_id.name}"
                        # )
            wizard.attribute_price = extra_price

    # Adjust computations to include the currency symbol
    @api.depends("product_price")
    def _compute_formatted_product_price(self):
        for wizard in self:
            if wizard.start_product_id:
                wizard.formatted_product_price = (
                    f"Price: {wizard.currency_id.symbol} {wizard.product_price:,.2f}"
                )
            else:
                wizard.formatted_product_price = ""

    @api.depends("attribute_price")
    def _compute_formatted_attribute_price(self):
        for wizard in self:
            if wizard.start_selected_attribute_value_ids:
                price_label = "+" if wizard.attribute_price > 0 else ""
                wizard.formatted_attribute_price = f"Price: {price_label}{wizard.currency_id.symbol} {wizard.attribute_price:,.2f}"
            else:
                wizard.formatted_attribute_price = ""

    @api.depends(
        "start_product_price",
        "start_attribute_price",
        "configure_product_price",
        "configure_attribute_price",
    )
    def _compute_running_total_price(self):
        for wizard in self:
            wizard.running_total_price = (
                wizard.start_product_price
                + wizard.start_attribute_price
                + wizard.configure_product_price
                + wizard.configure_attribute_price
            )

    @api.onchange("start_selected_attribute_value_ids")
    def _onchange_start_selected_attribute_value_ids(self):
        """Recompute prices when attributes are selected."""
        _logger.info(
            f"Attributes selected: {self.start_selected_attribute_value_ids.ids}"
        )
        self._compute_price()
        self._compute_formatted_total_price()
        _logger.info(f"Updated computed price: {self.computed_price}")
        _logger.info(f"Updated formatted total price: {self.formatted_total_price}")

    @api.depends(
        "start_product_price",
        "start_attribute_price",
        "configure_product_price",
        "configure_attribute_price",
    )
    def _compute_price(self):
        for wizard in self:
            wizard.computed_price = (
                wizard.start_product_price
                + wizard.start_attribute_price
                + wizard.configure_product_price
                + wizard.configure_attribute_price
            )

    @api.depends(
        "start_product_price",
        "start_attribute_price",
        "configure_product_price",
        "configure_attribute_price",
    )
    def _compute_formatted_total_price(self):
        for wizard in self:
            total_price = (
                wizard.start_product_price
                + wizard.start_attribute_price
                + wizard.configure_product_price
                + wizard.configure_attribute_price
            )
            wizard.formatted_total_price = (
                f"{wizard.currency_id.symbol} {total_price:,.2f}"
            )

    @api.depends("start_product_id")
    def _compute_available_attribute_values(self):
        for wizard in self:
            if wizard.start_product_id:
                wizard.available_attribute_values = (
                    wizard.start_product_id.product_tmpl_id.attribute_line_ids.mapped(
                        "value_ids"
                    )
                )
            else:
                wizard.available_attribute_values = self.env["product.attribute.value"]

    # Trigger price computation on attribute change
    @api.onchange("start_selected_attribute_value_ids", "start_product_id")
    def _onchange_attributes(self):
        self._compute_price()
        self._compute_formatted_total_price()

    def _get_product_domain(self, section=None):
        """Get domain for product selection based on section."""
        section = section or self.state
        configuration = self.env["wizard.section.configuration"].search(
            [("section_name", "=", section)], limit=1
        )
        if configuration and configuration.product_category_id:
            return [
                ("categ_id", "child_of", configuration.product_category_id.id),
                ("sale_ok", "=", True),
            ]
        return [("sale_ok", "=", True)]

    @api.onchange("start_product_id")
    def _onchange_start_product_id(self):
        """Load attributes for the selected Start Product."""
        if self.start_product_id:
            attribute_values = (
                self.start_product_id.product_tmpl_id.attribute_line_ids.mapped(
                    "value_ids"
                )
            )
            _logger.info(f"Available Start Attributes: {attribute_values.ids}")
            return {
                "domain": {
                    "start_selected_attribute_value_ids": [
                        ("id", "in", attribute_values.ids)
                    ]
                }
            }
        return {"domain": {"start_selected_attribute_value_ids": [("id", "=", False)]}}

    @api.onchange("configure_product_id")
    def _onchange_configure_product_id(self):
        """Load attributes for the selected Configure Product."""
        if self.configure_product_id:
            attribute_values = (
                self.configure_product_id.product_tmpl_id.attribute_line_ids.mapped(
                    "value_ids"
                )
            )
            _logger.info(f"Available Configure Attributes: {attribute_values.ids}")
            return {
                "domain": {
                    "configure_selected_attribute_value_ids": [
                        ("id", "in", attribute_values.ids)
                    ]
                }
            }
        return {
            "domain": {"configure_selected_attribute_value_ids": [("id", "=", False)]}
        }

    @api.depends(
        "start_product_id",
        "start_selected_attribute_value_ids",
        "configure_product_id",
        "configure_selected_attribute_value_ids",
    )
    def _compute_summary(self):
        for wizard in self:
            summary_lines = []

            if wizard.start_product_id:
                summary_lines.append(
                    f"Start Product: {wizard.start_product_id.name} (${wizard.product_price:.2f})"
                )
            if wizard.start_selected_attribute_value_ids:
                start_attributes = ", ".join(
                    wizard.start_selected_attribute_value_ids.mapped("name")
                )
                summary_lines.append(
                    f"Start Attributes: {start_attributes} (${wizard.attribute_price:.2f})"
                )

            if wizard.configure_product_id:
                summary_lines.append(
                    f"Configure Product: {wizard.configure_product_id.name} (${wizard.product_price:.2f})"
                )
            if wizard.configure_selected_attribute_value_ids:
                configure_attributes = ", ".join(
                    wizard.configure_selected_attribute_value_ids.mapped("name")
                )
                summary_lines.append(
                    f"Configure Attributes: {configure_attributes} (${wizard.attribute_price:.2f})"
                )

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

    def state_exit_start(self):
        """Transition from Start state."""
        if not self.start_product_id:
            raise ValidationError(_("Please select a product in the Start section."))

        # Log selected product
        _logger.info(
            f"Exiting Start state with product: {self.start_product_id.display_name}"
        )

        # Reset Configure section fields
        self.configure_product_id = False
        self.configure_selected_attribute_value_ids = [(5, 0, 0)]
        self.configure_product_price = 0.0
        self.configure_attribute_price = 0.0

        _logger.info(f"Exiting Start state with product: {self.start_product_id}")
        self.reset_section()
        # Move to Configure state
        self.state = "configure"

    def state_exit_configure(self):
        """Transition from Configure state."""
        if not self.configure_product_id:
            raise ValidationError(
                _("Please select a product in the Configure section.")
            )

        # Log selected product
        _logger.info(
            f"Exiting Configure state with product: {self.configure_product_id.display_name}"
        )

        # Reset Custom section fields if necessary
        self.field3 = ""

        _logger.info(
            f"Exiting Configure state with product: {self.configure_product_id}"
        )
        self.reset_section()

        # Move to Custom state
        self.state = "custom"

    def state_exit_custom(self):
        """Move to the summary state."""
        _logger.info(f"Field3 value before transition: {self.field3}")
        if not self.field3:
            raise ValidationError(_("Please enter customization details."))
        self.state = "summary"

    def state_exit_final(self):
        """Save wizard selections to the sales order line."""
        _logger.info(
            f"Finalizing wizard with: start_product_id={self.start_product_id}, configure_product_id={self.configure_product_id}, field3={self.field3}"
        )

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

    def reset_section(self):
        """Reset selections and prices for the current section."""
        if self.state == "start":
            self.start_product_id = False
            self.start_selected_attribute_value_ids = [(5, 0, 0)]
        elif self.state == "configure":
            self.configure_product_id = False
            self.configure_selected_attribute_value_ids = [(5, 0, 0)]

    @api.model
    def create(self, vals):
        """Ensure product_id is set when the wizard is created."""
        wizard = super().create(vals)
        if not wizard.product_id:
            domain = wizard._get_product_domain(wizard.state)
            default_product = wizard.env["product.product"].search(domain, limit=1)
            if default_product:
                wizard.product_id = default_product
            else:
                raise ValidationError(
                    _("No products available for the selected category.")
                )
        return wizard
