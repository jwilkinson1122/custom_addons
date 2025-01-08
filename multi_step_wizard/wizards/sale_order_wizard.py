import logging
import json
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class WizardSectionConfiguration(models.Model):
    _name = "wizard.section.configuration"
    _description = "Wizard Section Configuration"

    section_name = fields.Selection(
        [
            ("shell_foundation", "Shell / Foundation"),
            ("arch_height", "Arch Height"),
            ("top_cover", "Top Cover"),
            ("bottom_cover", "X-Guard"),
            ("cushion", "Cushion"),
            ("extension", "Extension"),
            ("options", "Options"),
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
    _description = "Sale Order Wizard"

    # General Fields
    sale_order_id = fields.Many2one(
        "sale.order",
        string="Sales Order",
        required=True,
        ondelete="cascade",
        default=lambda self: self.env.context.get("active_id"),
    )

    # Section Fields
    # section_product_id = fields.Many2one(
    #     "product.product",
    #     string="Section Product",
    #     domain=lambda self: self._get_product_domain(),
    #     help="Product selection for the current section.",
    # )

    section_product_id = fields.Many2one(
        "product.product",
        string="Section Product",
        domain="[('id', 'in', available_product_ids)]",  # Changed domain to use computed field
        help="Product selection for the current section.",
    )

    available_product_ids = fields.Many2many(
        "product.product",
        compute="_compute_available_products",
        help="Products available for selection in current section",
    )

    section_attribute_ids = fields.Many2many(
        "product.attribute.value",
        string="Section Attributes",
        help="Attributes belonging to the selected product.",
    )

    available_attribute_values = fields.Many2many(
        "product.attribute.value",
        string="Available Attributes",
        compute="_compute_available_attribute_values",
    )

    section_price = fields.Float(
        string="Section Price",
        compute="_compute_section_price",
        readonly=True,
    )

    # Total Prices
    total_price = fields.Float(
        string="Total Price",
        compute="_compute_total_price",
        readonly=True,
    )

    running_total_price = fields.Float(
        string="Running Total",
        compute="_compute_running_total_price",
        store=True,
    )

    formatted_total_price = fields.Char(
        string="Formatted Total Price",
        compute="_compute_formatted_total_price",
        readonly=True,
    )

    # Summary
    summary = fields.Text(
        string="Summary of Selections",
        compute="_compute_summary",
        readonly=True,
    )

    @api.depends("state")
    def _compute_state_display(self):
        for record in self:
            if record.state:
                # Replace underscores with spaces and capitalize each word
                record.state_display = record.state.replace("_", " ").title()
            else:
                record.state_display = ""

    state_display = fields.Char(
        string="State Display", compute="_compute_state_display"
    )

    @api.depends("section_data")
    def _compute_total_price(self):
        for wizard in self:
            _logger.debug(
                f"Computing total price for section_data: {wizard.section_data}"
            )
            wizard.total_price = 0.0
            if isinstance(wizard.section_data, dict):
                wizard.total_price = sum(
                    section.get("section_price", 0.0)
                    for section in wizard.section_data.values()
                )

    @api.depends("section_product_id", "section_attribute_ids")
    def _compute_section_price(self):
        """Compute the price for the current section based on product and attributes."""
        for wizard in self:
            product_price = (
                wizard.section_product_id.list_price
                if wizard.section_product_id
                else 0.0
            )
            attribute_price = sum(
                self.env["product.template.attribute.value"]
                .search(
                    [
                        (
                            "product_tmpl_id",
                            "=",
                            wizard.section_product_id.product_tmpl_id.id,
                        ),
                        (
                            "product_attribute_value_id",
                            "in",
                            wizard.section_attribute_ids.ids,
                        ),
                    ]
                )
                .mapped("price_extra")
            )
            wizard.section_price = product_price + attribute_price

    @api.depends("state", "section_data")
    def _compute_running_total_price(self):
        for wizard in self:
            total = 0.0
            try:
                # Force section_data to be a dict if it's not
                if not isinstance(wizard.section_data, dict):
                    wizard.section_data = {}
                    continue  # Skip processing this iteration

                if wizard.section_data:  # Only process if we have data
                    states = wizard._get_state_list()
                    current_state_index = (
                        states.index(wizard.state) if wizard.state in states else -1
                    )

                    for state in states[: current_state_index + 1]:
                        state_data = wizard.section_data.get(state, {})
                        if isinstance(state_data, dict):
                            price = state_data.get("section_price", 0.0)
                            try:
                                total += float(price or 0.0)
                            except (ValueError, TypeError):
                                continue
            except Exception as e:
                _logger.error(f"Error computing running total: {str(e)}")
                total = 0.0

            wizard.running_total_price = total

    @api.depends("running_total_price")
    def _compute_formatted_total_price(self):
        """Format the running total price."""
        for wizard in self:
            wizard.formatted_total_price = f"${wizard.running_total_price:,.2f}"

    @api.model
    def create(self, vals):
        # Initialize section_data before creation
        if "section_data" not in vals or not vals["section_data"]:
            vals["section_data"] = {}
        return super().create(vals)

    def write(self, vals):
        if "section_data" in vals:
            if not isinstance(vals["section_data"], dict):
                vals["section_data"] = {}
        return super().write(vals)

    @api.depends("section_data")
    def _compute_summary(self):
        """Generate a summary of all section selections."""
        for wizard in self:
            summary_lines = []
            if isinstance(wizard.section_data, dict):
                for state, data in wizard.section_data.items():
                    product_name = (
                        self.env["product.product"]
                        .browse(data.get("product_id"))
                        .display_name
                    )
                    attributes = ", ".join(
                        self.env["product.attribute.value"]
                        .browse(data.get("attribute_ids", []))
                        .mapped("name")
                    )
                    summary_lines.append(
                        f"{state.capitalize()}: {product_name} ({attributes})"
                    )
            wizard.summary = "\n".join(summary_lines)

    # def _build_product_domain(self, base_domain=None):
    #     """Helper method to build product domain."""
    #     domain = base_domain or [("sale_ok", "=", True)]

    #     def add_category_domain(category_id):
    #         if category_id:
    #             domain.append(("categ_id", "child_of", category_id))
    #         return bool(category_id)

    #     def add_laterality_domain():
    #         if self.laterality in ["left", "right"]:
    #             domain.append(("laterality", "=", self.laterality))

    #     configuration = self.env["wizard.section.configuration"].search(
    #         [("section_name", "=", self.state)], limit=1
    #     )
    #     if configuration and add_category_domain(configuration.product_category_id.id):
    #         add_laterality_domain()
    #         return domain

    #     category_name = self._state_category_mapping.get(self.state)
    #     if category_name:
    #         category = self.env["product.category"].search(
    #             [("name", "=", category_name)], limit=1
    #         )
    #         if category and add_category_domain(category.id):
    #             add_laterality_domain()
    #             return domain

    #     return [("id", "=", False)]

    def _build_product_domain(self, base_domain=None):
        """Helper method to build product domain."""
        domain = base_domain or [("sale_ok", "=", True)]

        def add_category_domain(category_id):
            if category_id:
                domain.append(("categ_id", "child_of", category_id))
                _logger.info(f"Added category domain with ID: {category_id}")
            return bool(category_id)

        # Try configuration first
        configuration = self.env["wizard.section.configuration"].search(
            [("section_name", "=", self.state)], limit=1
        )
        _logger.info(f"Found configuration for state '{self.state}': {configuration}")

        if configuration:
            _logger.info(
                f"Configuration category: {configuration.product_category_id.name}"
            )

        if configuration and add_category_domain(configuration.product_category_id.id):
            _logger.info(
                f"Using configuration category: {configuration.product_category_id.name}"
            )
            return domain

        # Fallback to category mapping
        category_name = self._state_category_mapping.get(self.state)
        _logger.info(f"Fallback category name: {category_name}")

        if category_name:
            category = self.env["product.category"].search(
                [("name", "=", category_name)], limit=1
            )
            _logger.info(
                f"Found fallback category: {category.name if category else 'None'}"
            )

            if category and add_category_domain(category.id):
                return domain

        _logger.info("No valid category found, returning empty domain")
        return [("id", "=", False)]

    @api.model
    def _get_product_domain(self):
        """Get domain for filtering products based on current state and laterality."""
        if not self.state or self.state in ["summary", "final"]:
            return [("id", "=", False)]

        domain = self._build_product_domain()
        _logger.debug(f"Product domain for state '{self.state}': {domain}")
        return domain

    # @api.onchange("state", "laterality")
    # def _onchange_state_laterality(self):
    #     """Clear product selection when state or laterality changes."""
    #     old_product = self.section_product_id
    #     self.section_product_id = False

    #     products = self.env["product.product"].search(self._get_product_domain())

    #     _logger.debug(
    #         f"""
    #         State/Laterality Change Debug:
    #         - Old State: {self._origin.state}
    #         - New State: {self.state}
    #         - Laterality: {self.laterality}
    #         - Available Products: {len(products)}
    #         - Product Names: {products.mapped('name')}
    #         - Old Product: {old_product.name if old_product else 'None'}
    #     """
    #     )

    @api.onchange("state", "laterality")
    def _onchange_state_laterality(self):
        """Clear product selection when state or laterality changes."""
        old_product = self.section_product_id
        self.section_product_id = False

        # Force compute of available products
        self._compute_available_products()

        _logger.info(
            f"""
            State/Laterality Change:
            - State: {self.state}
            - Laterality: {self.laterality}
            - Available Products: {len(self.available_product_ids)}
            - Product Names: {self.available_product_ids.mapped('name')}
            - Domain: {[('id', 'in', self.available_product_ids.ids)]}
        """
        )

    def action_verify_products(self):
        """Verify product configuration"""
        config = self.env["wizard.section.configuration"].search(
            [("section_name", "=", "shell_foundation")], limit=1
        )
        if config and config.product_category_id:
            products = self.env["product.product"].search(
                [
                    ("categ_id", "child_of", config.product_category_id.id),
                    ("sale_ok", "=", True),
                ]
            )
            _logger.info(
                f"""
                Product Verification:
                Category: {config.product_category_id.name}
                Products Found: {len(products)}
                Product Details:
                {[(p.name, p.categ_id.name, p.sale_ok, p.active) for p in products]}
            """
            )

    @api.constrains("state", "section_product_id")
    def _check_product_category(self):
        for record in self:
            if record.section_product_id and record.state not in ["summary", "final"]:
                category_name = record._state_category_mapping.get(record.state)
                category = record.env["product.category"].search(
                    [("name", "=", category_name)], limit=1
                )
                if category and record.section_product_id.categ_id != category:
                    raise ValidationError(
                        _(
                            "Selected product must belong to the %s category in %s state."
                        )
                        % (category_name, record.state)
                    )

    @api.depends("state")
    def _compute_current_category_id(self):
        """Compute the current category ID based on state"""
        for record in self:
            configuration = self.env["wizard.section.configuration"].search(
                [("section_name", "=", record.state)], limit=1
            )
            record.current_category_id = (
                configuration.product_category_id.id if configuration else False
            )

    current_category_id = fields.Many2one(
        "product.category",
        compute="_compute_current_category_id",
        help="Current product category based on wizard state",
    )

    @api.depends("state", "laterality")
    def _compute_available_products(self):
        """Compute available products based on current state and laterality"""
        for record in self:
            if record.state in ["summary", "final"]:
                record.available_product_ids = [(5, 0, 0)]
            else:
                domain = record._build_product_domain()
                products = self.env["product.product"].search(domain)
                record.available_product_ids = products.ids
                _logger.info(
                    f"""
                    Available Products Computed:
                    - State: {record.state}
                    - Domain: {domain}
                    - Products Found: {len(products)}
                    - Product Names: {products.mapped('name')}
                """
                )

    @api.depends("section_product_id")
    def _compute_available_attribute_values(self):
        """Compute the available attribute values for the selected product."""
        for wizard in self:
            if wizard.section_product_id:
                # Get attribute values from the product template's attribute lines
                valid_attr_values = (
                    self.env["product.template.attribute.value"]
                    .search(
                        [
                            (
                                "product_tmpl_id",
                                "=",
                                wizard.section_product_id.product_tmpl_id.id,
                            )
                        ]
                    )
                    .mapped("product_attribute_value_id")
                )
                wizard.available_attribute_values = valid_attr_values
            else:
                wizard.available_attribute_values = self.env["product.attribute.value"]

    @api.onchange("section_product_id", "section_attribute_ids")
    def _onchange_section_selections(self):
        self.ensure_one()
        if not isinstance(self.section_data, dict):
            self.section_data = {}

    @api.model
    def _init_record(self, values):
        """Initialize a new record with proper defaults."""
        if "section_data" not in values:
            values["section_data"] = {}
        if "state" not in values:
            values["state"] = "shell_foundation"
        if "laterality" not in values:
            values["laterality"] = "bilateral"
        return values

    @api.onchange("section_product_id")
    def _onchange_section_product_id(self):
        """Update section attributes when product changes"""
        self.section_attribute_ids = False  # Clear existing attributes
        if self.section_product_id:
            # Get all possible attribute values for this product
            valid_attr_values = (
                self.env["product.template.attribute.value"]
                .search(
                    [
                        (
                            "product_tmpl_id",
                            "=",
                            self.section_product_id.product_tmpl_id.id,
                        )
                    ]
                )
                .mapped("product_attribute_value_id")
            )

            # Set the domain for section_attribute_ids
            return {
                "domain": {
                    "section_attribute_ids": [("id", "in", valid_attr_values.ids)]
                }
            }

    def reset_section(self):
        """Reset selections for the current section."""
        _logger.info(f"Resetting section '{self.state}' for wizard {self.id}.")
        self.section_product_id = False
        self.section_attribute_ids = [(5, 0, 0)]
        self.section_price = 0.0
        if self.state in self.section_data:
            del self.section_data[self.state]  # Clear saved data for this section

    def _update_section_data(self):
        """Safely update section data for the current state."""
        try:
            if not self.section_data or isinstance(self.section_data, bool):
                self.section_data = {}

            if self.state:
                self.section_data[self.state] = {
                    "section_price": self.section_price,
                    "product_id": (
                        self.section_product_id.id if self.section_product_id else False
                    ),
                    "attribute_ids": (
                        self.section_attribute_ids.ids
                        if self.section_attribute_ids
                        else []
                    ),
                }
        except Exception as e:
            _logger.error("Error updating section data: %s", str(e))

    @api.model
    def default_get(self, fields_list):
        """Ensure section_data is properly initialized."""
        defaults = super().default_get(fields_list)
        if "section_data" in fields_list:
            _logger.debug(f"Default section_data value: {defaults.get('section_data')}")
            defaults["section_data"] = {}
        return defaults

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if "section_data" in fields_list:
            defaults["section_data"] = {}
        return defaults

    def submit_wizard(self):
        """Submit wizard selections and create sale order lines."""
        if not self.sale_order_id:
            raise ValidationError(_("No associated sales order found."))

        if not self.section_data:
            raise ValidationError(_("The wizard contains no selections to submit."))

        _logger.info(
            f"Finalizing submission for Sale Order ID: {self.sale_order_id.id}"
        )
        _logger.debug(f"Section Data: {self.section_data}")

        for state, data in self.section_data.items():
            product_id = data.get("product_id")
            laterality = data.get("laterality", "N/A")
            section_price = data.get("section_price", 0.0)
            description = (
                f"{state.replace('_', ' ').title()}:\n"
                f"- Laterality: {laterality}\n"
                f"- Price: ${section_price:,.2f}"
            )

            if not product_id:
                _logger.warning(f"No product found for section {state}. Skipping.")
                continue

            product = self.env["product.product"].browse(product_id)
            self.env["sale.order.line"].create(
                {
                    "order_id": self.sale_order_id.id,
                    "product_id": product_id,
                    "product_uom_qty": 1,
                    "price_unit": section_price,
                    "name": description,
                }
            )

        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "res_id": self.sale_order_id.id,
            "view_mode": "form",
            "target": "current",
        }
