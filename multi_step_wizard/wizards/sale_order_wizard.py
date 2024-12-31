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
        # required=True,
    )

    product_template_id = fields.Many2one(
        comodel_name="product.template",
        string="Product Template",
        compute="_compute_product_template",
        store=True,
    )

    # Section-specific fields
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

    @api.onchange("start_product_id")
    def _onchange_start_product_id(self):
        """Update the domain for Start Attributes based on the selected Start Product."""
        if self.start_product_id:
            # Get attribute values related to the selected product
            attribute_values = (
                self.start_product_id.product_tmpl_id.attribute_line_ids.mapped(
                    "value_ids"
                )
            )
            _logger.info(f"Start Product Attribute Values: {attribute_values.ids}")
            return {
                "domain": {
                    "start_selected_attribute_value_ids": [
                        ("id", "in", attribute_values.ids)
                    ]
                }
            }
        else:
            _logger.info("No Start Product Selected, resetting attributes.")
            return {
                "domain": {"start_selected_attribute_value_ids": [("id", "=", False)]}
            }

    @api.onchange("configure_product_id")
    def _onchange_configure_product_id(self):
        """Update the domain for Configure Attributes based on the selected Configure Product."""
        if self.configure_product_id:
            attribute_values = (
                self.configure_product_id.product_tmpl_id.attribute_line_ids.mapped(
                    "value_ids"
                )
            )
            _logger.info(f"Configure Product Attribute Values: {attribute_values.ids}")
            return {
                "domain": {
                    "configure_selected_attribute_value_ids": [
                        ("id", "in", attribute_values.ids)
                    ]
                }
            }
        else:
            _logger.info("No Configure Product Selected, resetting attributes.")
            return {
                "domain": {
                    "configure_selected_attribute_value_ids": [("id", "=", False)]
                }
            }

    def _get_product_domain(self, section=None):
        """Get domain for a specific section."""
        section = section or self.state  # Use current state if section is None
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
            return {"domain": {"start_product_id": domain}}
        elif self.state == "configure":
            self.configure_product_id = None
            return {"domain": {"configure_product_id": domain}}
        return {}

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

    product_variant_id = fields.Many2one(
        comodel_name="product.product",
        string="Product Variant",
        compute="_compute_product_variant",
        store=True,
    )

    field1 = fields.Char(string="Configuration 1", default="N/A")
    field2 = fields.Char(string="Configuration 2", default="N/A")
    field3 = fields.Char(string="Customization", default="N/A")

    computed_price = fields.Float(
        string="Computed Price", compute="_compute_price", store=True, default=0.0
    )

    @api.depends(
        "start_product_id",
        "start_selected_attribute_value_ids",
        "configure_product_id",
        "configure_selected_attribute_value_ids",
    )
    def _compute_price(self):
        for wizard in self:
            base_price = 0.0
            extra_price = 0.0

            def calculate_attribute_price(product, selected_attributes):
                price = 0.0
                if product:
                    for attribute in selected_attributes:
                        template_value = self.env[
                            "product.template.attribute.value"
                        ].search(
                            [
                                ("product_tmpl_id", "=", product.product_tmpl_id.id),
                                ("product_attribute_value_id", "=", attribute.id),
                            ],
                            limit=1,
                        )
                        price += template_value.price_extra if template_value else 0.0
                return price

            if wizard.start_product_id:
                base_price += wizard.start_product_id.list_price
                extra_price += calculate_attribute_price(
                    wizard.start_product_id, wizard.start_selected_attribute_value_ids
                )

            if wizard.configure_product_id:
                base_price += wizard.configure_product_id.list_price
                extra_price += calculate_attribute_price(
                    wizard.configure_product_id,
                    wizard.configure_selected_attribute_value_ids,
                )

            wizard.computed_price = base_price + extra_price

    # @api.depends(
    #     "start_product_id",
    #     "start_selected_attribute_value_ids",
    #     "configure_product_id",
    #     "configure_selected_attribute_value_ids",
    # )
    # def _compute_price(self):
    #     for wizard in self:
    #         base_price = 0.0
    #         extra_price = 0.0

    #         def calculate_attribute_price(product, selected_attributes):
    #             price = 0.0
    #             if product:
    #                 for attribute in selected_attributes:
    #                     template_value = self.env[
    #                         "product.template.attribute.value"
    #                     ].search(
    #                         [
    #                             ("product_tmpl_id", "=", product.product_tmpl_id.id),
    #                             ("product_attribute_value_id", "=", attribute.id),
    #                         ],
    #                         limit=1,
    #                     )
    #                     price += template_value.price_extra if template_value else 0.0
    #             return price

    #         if wizard.start_product_id:
    #             base_price += wizard.start_product_id.list_price
    #             extra_price += calculate_attribute_price(
    #                 wizard.start_product_id, wizard.start_selected_attribute_value_ids
    #             )

    #         if wizard.configure_product_id:
    #             base_price += wizard.configure_product_id.list_price
    #             extra_price += calculate_attribute_price(
    #                 wizard.configure_product_id,
    #                 wizard.configure_selected_attribute_value_ids,
    #             )

    #         wizard.computed_price = base_price + extra_price

    # Add fields to display prices in the wizard
    # Currency field
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        required=True,
        # default=lambda self: self.sale_order_id.currency_id
        # or self.env.company.currency_id,
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
        string="Price", compute="_compute_formatted_total_price", readonly=True
    )

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

    # @api.depends("start_selected_attribute_value_ids", "start_product_id")
    # def _compute_attribute_price(self):
    #     for wizard in self:
    #         extra_price = 0.0
    #         if wizard.start_product_id:
    #             for attribute in wizard.start_selected_attribute_value_ids:
    #                 template_value = self.env[
    #                     "product.template.attribute.value"
    #                 ].search(
    #                     [
    #                         (
    #                             "product_tmpl_id",
    #                             "=",
    #                             wizard.start_product_id.product_tmpl_id.id,
    #                         ),
    #                         ("product_attribute_value_id", "=", attribute.id),
    #                     ],
    #                     limit=1,
    #                 )
    #                 if template_value:
    #                     _logger.info(
    #                         f"Attribute {attribute.name} Price Extra: {template_value.price_extra}"
    #                     )
    #                     extra_price += template_value.price_extra
    #                 else:
    #                     _logger.warning(
    #                         f"Attribute {attribute.name} not linked to product {wizard.start_product_id.name}"
    #                     )
    #         wizard.attribute_price = extra_price

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

    @api.depends("product_price", "attribute_price")
    def _compute_formatted_total_price(self):
        for wizard in self:
            total_price = wizard.product_price + wizard.attribute_price
            wizard.formatted_total_price = (
                f"{wizard.currency_id.symbol} {total_price:,.2f}"
            )

    summary_label = fields.Char(
        "Selection Summary Label",
        translate=True,
        default="Summary of Selections:",
        readonly=True,
    )

    summary = fields.Text(string="Summary", compute="_compute_summary", default="")

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

    # @api.depends("start_product_id")
    # def _compute_available_attribute_values(self):
    #     for wizard in self:
    #         if wizard.start_product_id:
    #             wizard.available_attribute_values = (
    #                 wizard.start_product_id.product_tmpl_id.attribute_line_ids.mapped(
    #                     "value_ids"
    #                 )
    #             )
    #         else:
    #             wizard.available_attribute_values = self.env["product.attribute.value"]

    # @api.depends("start_product_id")
    # def _compute_available_attribute_values(self):
    #     for wizard in self:
    #         if wizard.start_product_id:
    #             available_values = (
    #                 wizard.start_product_id.product_tmpl_id.attribute_line_ids.mapped(
    #                     "value_ids"
    #                 )
    #             )
    #             _logger.info(
    #                 f"Computed Available Attribute Values: {available_values.ids}"
    #             )
    #             wizard.available_attribute_values = available_values
    #         else:
    #             wizard.available_attribute_values = self.env["product.attribute.value"]

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

    # Ensure state-specific validation
    def state_exit_start(self):
        """Transition from Start state."""
        if not self.start_product_id:
            raise ValidationError(_("Please select a product in the Start section."))

        # Log the selected product for debugging
        _logger.info(
            f"Exiting Start state with product: {self.start_product_id.display_name} (ID: {self.start_product_id.id})"
        )

        # Validate that the product has linked attributes
        if not self.available_attribute_values:
            raise ValidationError(
                _(
                    "The selected product has no linked attributes. Please configure the product attributes before proceeding."
                )
            )

        # Transition to the 'configure' state
        self.state = "configure"

    # def state_exit_start(self):
    #     """Transition from Start section."""
    #     if not self.start_product_id:
    #         raise ValidationError(_("Please select a product in the Start section."))
    #     self.state = "configure"

    def state_exit_configure(self):
        """Transition from Configure state."""
        if not self.configure_product_id:
            raise ValidationError(
                _("Please select a product in the Configure section.")
            )
        _logger.info(
            f"Exiting Configure state with product: {self.configure_product_id.name}"
        )
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
