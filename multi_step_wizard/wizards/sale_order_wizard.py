import traceback
import logging
import json
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import format_amount

_logger = logging.getLogger(__name__)


class WizardSectionConfiguration(models.Model):
    _name = "wizard.section.configuration"
    _description = "Wizard Section Configuration"
    _order = "sequence"

    sequence = fields.Integer(string="Sequence", default=10)

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

    # Add helper method to get next section
    def get_next_section(self, current_section):
        sections = self.search([("section_name", "!=", "final")], order="sequence")
        section_list = sections.mapped("section_name")
        try:
            current_index = section_list.index(current_section)
            if current_index + 1 < len(section_list):
                return section_list[current_index + 1]
        except ValueError:
            pass
        return "final"

    _sql_constraints = [
        (
            "unique_section_name",
            "unique(section_name)",
            "Each section can only be linked to one product category.",
        ),
    ]


class WizardSectionSelection(models.TransientModel):
    _name = "wizard.section.selection"
    _description = "Wizard Section Selection"

    wizard_id = fields.Many2one(
        "sale.order.wizard", string="Wizard", required=True, ondelete="cascade"
    )

    section = fields.Selection(related="wizard_id.state", string="Section", store=True)

    section_product_id = fields.Many2one(
        "product.product", string="Product", domain=[("sale_ok", "=", True)]
    )

    section_attribute_ids = fields.Many2many(
        "product.attribute.value", string="Attributes"
    )

    price = fields.Float(string="Price", digits="Product Price", default=0.0)

    @api.model
    def create(self, vals):
        """Ensure proper initialization of values."""
        if "price" in vals:
            vals["price"] = float(vals.get("price", 0.0) or 0.0)
        return super().create(vals)

    def write(self, vals):
        """Ensure proper value updates."""
        if "price" in vals:
            vals["price"] = float(vals.get("price", 0.0) or 0.0)
        return super().write(vals)


class SaleOrderWizard(models.TransientModel):
    _name = "sale.order.wizard"
    _inherit = ["multi.step.wizard.mixin"]
    _description = "Sale Order Wizard"

    sale_order_id = fields.Many2one(
        "sale.order",
        string="Sales Order",
        # required=True,
        required=False,  # Change this to False
        ondelete="cascade",
        default=lambda self: self.env.context.get("active_id"),
    )

    section_selection_ids = fields.One2many(
        "wizard.section.selection", "wizard_id", string="Section Selections"
    )

    # Products
    section_product_id = fields.Many2one(
        "product.product",
        string="Product",
        domain="[('id', 'in', available_product_ids)]",
    )

    # available_product_ids = fields.Many2many(
    #     "product.product",
    #     "wizard_available_product_rel",
    #     "wizard_id",
    #     "product_id",
    #     string="Available Products",
    #     compute="_compute_available_products",
    #     store=True,
    # )

    available_product_ids = fields.Many2many(
        "product.product",
        string="Available Products",
        compute="_compute_available_products",
        store=False,
    )

    available_attribute_values = fields.Many2many(
        "product.attribute.value",
        string="Available Attribute Values",
        compute="_compute_available_attribute_values",
        store=False,
    )

    section_attribute_ids = fields.Many2many(
        "product.attribute.value",
        "wizard_section_attribute_rel",
        "wizard_id",
        "attribute_id",
        string="Selected Attributes",
        domain="[('id', 'in', available_attribute_values)]",
    )

    # Monetary fields definition
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        readonly=True,
        default=lambda self: self.env.company.currency_id.id,
    )

    section_price = fields.Float(
        string="Section Price",
        digits="Product Price",
        default=0.0,
        readonly=True,
    )

    total_price = fields.Float(
        string="Total Price",
        digits="Product Price",
        default=0.0,
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

    summary = fields.Text(
        string="Summary",
        compute="_compute_summary",
        store=True,
    )

    summary_total = fields.Float(
        string="Total Amount",
        compute="_compute_summary",
        store=True,
        digits="Product Price",
        default=0.0,
    )

    @api.model
    def create(self, values):
        """Initialize a new record with proper defaults and monetary values."""
        try:
            # Initialize record with defaults
            values = self._init_record(values)

            # Validate monetary fields
            monetary_fields = ["section_price", "total_price"]
            for field in monetary_fields:
                if field in values:
                    values[field] = self._validate_price(
                        values.get(field), field_name=field
                    )

            _logger.debug(
                f"""
                Creating record:
                - Values: {values}
                """
            )

            return super().create(values)

        except Exception as e:
            _logger.error(
                f"""
                Error creating record:
                - Values: {values}
                - Error: {str(e)}
                """
            )
            raise

    def write(self, vals):
        """Update record with proper handling of sections and monetary values."""
        try:
            # Handle state changes
            if "state" in vals:
                self._handle_state_change(vals)

            # Validate monetary fields
            monetary_fields = ["section_price", "total_price"]
            for field in monetary_fields:
                if field in vals:
                    vals[field] = self._validate_price(
                        vals.get(field), field_name=field
                    )

            _logger.debug(
                f"""
                Updating record:
                - ID: {self.id}
                - Values: {vals}
                """
            )

            return super().write(vals)

        except Exception as e:
            _logger.error(
                f"""
                Error updating record:
                - ID: {self.id}
                - Values: {vals}
                - Error: {str(e)}
                """
            )
            raise

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

    @api.onchange("state", "laterality")
    def _onchange_state(self):
        """Handle state and laterality changes."""
        self.ensure_one()

        # Clear products for summary/final states
        if self.state in ["summary", "final"]:
            self.available_product_ids = [(5, 0, 0)]
            self.section_product_id = False
            return

        try:
            # Get configuration for current state
            configuration = self.env["wizard.section.configuration"].search(
                [("section_name", "=", self.state)], limit=1
            )

            # Base domain
            domain = [("sale_ok", "=", True)]

            # Add category filter if configuration exists
            if configuration and configuration.product_category_id:
                domain.append(
                    ("categ_id", "child_of", configuration.product_category_id.id)
                )

            # Search for products matching domain
            products = self.env["product.product"].search(domain)

            # Apply laterality filter if specified
            if self.laterality in ["left", "right"]:
                products = products.filtered(
                    lambda p: p.laterality in [self.laterality, "bilateral"]
                )

            # Update available products
            self.available_product_ids = [(6, 0, products.ids)]

            # Clear current product if it's no longer valid
            if self.section_product_id and self.section_product_id not in products:
                self.section_product_id = False

            _logger.info(
                f"""
                State/Laterality Change Processed:
                - State: {self.state}
                - Laterality: {self.laterality}
                - Configuration Found: {bool(configuration)}
                - Category: {configuration.product_category_id.name if configuration and configuration.product_category_id else 'N/A'}
                - Domain: {domain}
                - Products Found: {len(products)}
                - Current Product Valid: {bool(self.section_product_id in products if self.section_product_id else False)}
                """
            )

        except Exception as e:
            _logger.error(
                f"""
                Error in state/laterality change:
                - State: {self.state}
                - Laterality: {self.laterality}
                - Error: {str(e)}
                """
            )
            # Clear products on error
            self.available_product_ids = [(5, 0, 0)]
            self.section_product_id = False

    def _handle_state_change(self, vals):
        """Handle state change logic."""
        # Clear current section fields when changing state
        vals.update(
            {
                "section_product_id": False,
                "section_attribute_ids": [(5, 0, 0)],
            }
        )

        # Load saved selection if exists
        if vals["state"] not in ["summary", "final"]:
            current_selection = self.section_selection_ids.filtered(
                lambda x: x.section == vals["state"]
            )
            if current_selection:
                vals.update(
                    {
                        "section_product_id": current_selection.product_id.id,
                        "section_attribute_ids": [
                            (6, 0, current_selection.attribute_ids.ids)
                        ],
                        "section_price": self._validate_price(
                            current_selection.price, field_name="section_price"
                        ),
                    }
                )

        _logger.debug(
            f"""
            State change handled:
            - New State: {vals['state']}
            - Selection Found: {bool(current_selection if 'current_selection' in locals() else False)}
            """
        )

    # Actions
    def action_verify_state_product(self):
        """Verify current state and product configuration"""
        self.ensure_one()

        # Get current selection
        current_selection = self.section_selection_ids.filtered(
            lambda x: x.section == self.state
        )

        # Get configuration
        configuration = self.env["wizard.section.configuration"].search(
            [("section_name", "=", self.state)], limit=1
        )

        _logger.info(
            f"""
            State and Product Verification:
            State: {self.state}
            State Display: {self.state_display}
            
            Current Selection:
            Product: {current_selection.product_id.name if current_selection.product_id else 'None'}
            Attributes: {current_selection.attribute_ids.mapped('name') if current_selection.attribute_ids else []}
            
            Working Fields:
            Product: {self.section_product_id.name if self.section_product_id else 'None'}
            Attributes: {self.section_attribute_ids.mapped('name') if self.section_attribute_ids else []}
            
            Configuration:
            Found: {bool(configuration)}
            Category: {configuration.product_category_id.name if configuration else 'None'}
        """
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Verification Complete"),
                "message": _("Check the logs for detailed information."),
                "type": "info",
                "sticky": False,
            },
        }

    def action_verify_products(self):
        try:
            config = self.env["wizard.section.configuration"].search(
                [("section_name", "=", "shell_foundation")], limit=1
            )
            if not config:
                _logger.warning("No configuration found for shell_foundation")
                return

            if not config.product_category_id:
                _logger.warning("No product category configured for shell_foundation")
                return

            # Rest of the code...
        except Exception as e:
            _logger.error(f"Error in product verification: {str(e)}")

    def action_debug_products(self):
        """Debug product filtering and availability.

        This method performs the following:
        - Retrieves products based on current domain
        - Logs detailed product information including laterality
        - Tests name_search functionality
        - Logs all results for debugging purposes
        """
        _logger.info("Starting product debugging session...")

        try:
            # Debug current domain and product search
            domain = self._get_product_domain()
            _logger.debug(f"Current product domain: {domain}")

            products = self.env["product.product"].search(domain)
            _logger.info(f"Found {len(products)} products matching domain")

            # Log detailed product information
            for product in products:
                self._log_product_details(product)

            # Test name_search functionality
            self._debug_name_search(products)

            # Debug product availability
            self._debug_product_availability(products)

            # Debug product categories
            self._debug_product_categories()

        except Exception as e:
            _logger.error(f"Error during product debugging: {str(e)}")
            raise

    def action_debug_domain(self):
        domain = self._get_product_domain()
        products = self.env["product.product"].search(domain)

        debug_info = {
            "state": self.state,
            "domain": domain,
            "products_count": len(products),
            "product_details": [
                (p.id, p.name, p.categ_id.name, p.sale_ok) for p in products
            ],
            "available_product_ids": self.available_product_ids.ids,
            "section_product": (
                self.section_product_id.name if self.section_product_id else "None"
            ),
        }

        _logger.info("Domain Debug: %s", json.dumps(debug_info, indent=2))

    def _log_product_details(self, product):
        """Log detailed information about a specific product."""
        _logger.info(
            f"""
            Product Details:
            - ID: {product.id}
            - Name: {product.name}
            - Internal Reference: {product.default_code or 'N/A'}
            - Category: {product.categ_id.name}
            - Type: {product.type}
            - List Price: {product.list_price}
            - Standard Price: {product.standard_price}
            - Active: {product.active}
            - Can be Sold: {product.sale_ok}
            - Can be Purchased: {product.purchase_ok}
            """
        )

    def _debug_name_search(self, products):
        """Test and log name_search functionality."""
        _logger.info("Testing name_search functionality...")

        for product in products[:5]:  # Test first 5 products
            name_results = self.env["product.product"].name_search(
                name=product.name, args=self._get_product_domain(), limit=5
            )
            _logger.info(
                f"""
                Name search results for '{product.name}':
                Found {len(name_results)} matches
                Results: {[f"{r[1]} (ID: {r[0]})" for r in name_results]}
                """
            )

    def _debug_product_availability(self, products):
        """Debug product availability and inventory levels."""
        _logger.info("Checking product availability...")

        for product in products:
            qty_available = product.qty_available
            virtual_available = product.virtual_available
            incoming_qty = product.incoming_qty
            outgoing_qty = product.outgoing_qty

            _logger.info(
                f"""
                Availability for {product.name} (ID: {product.id}):
                - Quantity on Hand: {qty_available}
                - Forecasted Quantity: {virtual_available}
                - Incoming: {incoming_qty}
                - Outgoing: {outgoing_qty}
                """
            )

    def _debug_product_categories(self):
        """Debug product category hierarchy and configurations."""
        _logger.info("Analyzing product categories...")

        categories = self.env["product.category"].search([])
        for category in categories:
            products_count = self.env["product.product"].search_count(
                [("categ_id", "=", category.id)]
            )

            _logger.info(
                f"""
                Category: {category.name} (ID: {category.id})
                - Complete Name: {category.complete_name}
                - Parent: {category.parent_id.name if category.parent_id else 'None'}
                - Products Count: {products_count}
                """
            )

    def _get_product_domain(self):
        """Get domain for filtering products based on current state and laterality."""
        self.ensure_one()

        # Return empty domain for summary/final states
        if not self.state or self.state in ["summary", "final"]:
            return [("id", "=", False)]

        try:
            # Start with base domain
            domain = [
                ("sale_ok", "=", True),
                ("active", "=", True),  # Always filter for active products
            ]

            # Get configuration for current state
            configuration = self.env["wizard.section.configuration"].search(
                [("section_name", "=", self.state)], limit=1
            )

            if not configuration or not configuration.product_category_id:
                _logger.warning(
                    f"""
                    No valid configuration found:
                    - State: {self.state}
                    - Configuration Found: {bool(configuration)}
                    - Has Category: {bool(configuration.product_category_id if configuration else False)}
                    """
                )
                return [("id", "=", False)]

            # Add category domain using child_of operator
            domain.append(
                ("categ_id", "child_of", configuration.product_category_id.id)
            )

            # Add laterality filter if applicable
            if hasattr(self, "laterality") and self.laterality in ["left", "right"]:
                domain.extend(
                    [
                        "|",
                        ("laterality", "=", self.laterality),
                        ("laterality", "=", "bilateral"),
                    ]
                )

            # Add custom active filter if different from default
            if hasattr(self, "active_filter") and not self.active_filter:
                domain[1] = ("active", "=", False)

            _logger.info(
                f"""
                Product Domain Built:
                - State: {self.state}
                - Category: {configuration.product_category_id.display_name}
                - Laterality: {getattr(self, 'laterality', 'N/A')}
                - Configuration ID: {configuration.id}
                - Domain: {domain}
                """
            )

            return domain

        except Exception as e:
            _logger.error(
                f"""
                Error building product domain:
                - State: {self.state}
                - Error: {str(e)}
                - Traceback: {traceback.format_exc()}
                """
            )
            return [("id", "=", False)]

    def action_verify_current_configuration(self):
        """Verify configuration for current state"""
        configuration = self.env["wizard.section.configuration"].search(
            [("section_name", "=", self.state)], limit=1
        )

        _logger.info(
            f"""
            Current Section Configuration:
            State: {self.state}
            Configuration Found: {bool(configuration)}
            Category: {configuration.product_category_id.name if configuration else 'None'}
            Selected Product: {self.section_product_id.name if self.section_product_id else 'None'}
            Product Category: {self.section_product_id.categ_id.name if self.section_product_id else 'None'}
        """
        )

    def action_verify_all_configurations(self):
        """Verify all section configurations"""
        configs = self.env["wizard.section.configuration"].search([])
        for config in configs:
            _logger.info(
                f"""
                Configuration:
                Section: {config.section_name}
                Category: {config.product_category_id.name}
                Category ID: {config.product_category_id.id}
            """
            )

    @api.constrains("state", "section_product_id", "section_selection_ids")
    def _check_product_category(self):
        """Validate that selected product belongs to the correct category for the current state."""
        for record in self:
            if record.state in ["summary", "final"]:
                continue

            # Validate current selection
            if record.section_product_id:
                self._validate_product_category(
                    record.state, record.section_product_id, record.state_display
                )

            # Validate all stored selections
            for selection in record.section_selection_ids:
                if selection.product_id:
                    self._validate_product_category(
                        selection.section,
                        selection.product_id,
                        selection.section.replace("_", " ").title(),
                    )

    def _validate_product_category(self, state, product, state_display):
        """Helper method to validate product category against section configuration."""
        configuration = self.env["wizard.section.configuration"].search(
            [("section_name", "=", state)], limit=1
        )

        if not configuration:
            _logger.error(f"No configuration found for state: {state}")
            raise ValidationError(_("No configuration found for state %s") % state)

        expected_category = configuration.product_category_id
        actual_category = product.categ_id

        _logger.info(
            f"""
            Category Validation Details:
            State: {state}
            Product: {product.name}
            Product Category ID: {actual_category.id}
            Expected Category ID: {expected_category.id}
            Product Category: {actual_category.name}
            Expected Category: {expected_category.name}
            Product Category Path: {actual_category.parent_path}
            Expected Category Path: {expected_category.parent_path}
        """
        )

        if (
            actual_category.id != expected_category.id
            and not actual_category.parent_path.startswith(
                expected_category.parent_path
            )
        ):
            raise ValidationError(
                _(
                    "Selected product '%(product)s' (category: %(actual)s) must belong to "
                    "the '%(expected)s' category in %(state)s state."
                )
                % {
                    "product": product.name,
                    "actual": actual_category.name,
                    "expected": expected_category.name,
                    "state": state_display,
                }
            )

    @api.depends("state")
    def _compute_current_category_id(self):
        """Compute the current product category based on state."""
        for record in self:
            try:
                if not record.state or record.state in ["summary", "final"]:
                    record.current_category_id = False
                    continue

                # Search for configuration in a new environment to avoid transaction issues
                self.env.cr.rollback()  # Roll back any failed transaction

                configuration = (
                    self.env["wizard.section.configuration"]
                    .sudo()
                    .search(
                        [("section_name", "=", record.state)],
                        limit=1,
                    )
                )

                record.current_category_id = (
                    configuration.product_category_id.id if configuration else False
                )

                _logger.debug(
                    f"""
                    Category Computed:
                    - State: {record.state}
                    - Configuration Found: {bool(configuration)}
                    - Category ID: {record.current_category_id}
                    """
                )

            except Exception as e:
                _logger.error(
                    f"""
                    Error computing category:
                    - State: {record.state}
                    - Error: {str(e)}
                    """
                )
                record.current_category_id = False

    # current_category_id = fields.Many2one(
    #     "product.category",
    #     string="Current Category",
    #     compute="_compute_current_category_id",
    #     store=False,
    #     readonly=True,
    # )

    current_category_id = fields.Many2one(
        "product.category",
        string="Current Category",
        compute="_compute_current_category_id",
        store=False,
    )

    @api.onchange("state")
    def _onchange_current_category(self):
        """Update domain and selections when state changes"""
        if self.state not in ["summary", "final"]:
            return {"domain": {"section_product_id": self._get_product_domain()}}

    def action_validate_all_selections(self):
        """Validate all selections at once"""
        self.ensure_one()
        for selection in self.section_selection_ids:
            self._validate_product_category(
                selection.section,
                selection.product_id,
                selection.section.replace("_", " ").title(),
            )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Validation Success"),
                "message": _("All selections are valid."),
                "type": "success",
                "sticky": False,
            },
        }

    @api.depends("state", "laterality")
    def _compute_available_products(self):
        """Compute available products based on current state and laterality."""
        for record in self:
            try:
                # Clear products for summary/final states
                if not record.state or record.state in ["summary", "final"]:
                    record.available_product_ids = False
                    continue

                # Get configuration for current state
                configuration = self.env["wizard.section.configuration"].search(
                    [("section_name", "=", record.state)], limit=1
                )

                if not configuration or not configuration.product_category_id:
                    record.available_product_ids = False
                    continue

                # Build domain
                domain = [
                    ("sale_ok", "=", True),
                    ("active", "=", True),
                    ("categ_id", "child_of", configuration.product_category_id.id),
                ]

                # Add laterality filter if applicable
                if record.laterality in ["left", "right"]:
                    domain.extend(
                        [
                            "|",
                            ("laterality", "=", record.laterality),
                            ("laterality", "=", "bilateral"),
                        ]
                    )

                # Search products
                products = self.env["product.product"].search(domain)

                _logger.debug(
                    f"""
                    Available Products Computed:
                    - State: {record.state}
                    - Category: {configuration.product_category_id.display_name}
                    - Products Found: {len(products)}
                    - Product IDs: {products.ids}
                    """
                )

                record.available_product_ids = products

            except Exception as e:
                _logger.error(
                    f"""
                    Error computing available products:
                    - State: {record.state}
                    - Error: {str(e)}
                    - Traceback: {traceback.format_exc()}
                    """
                )
                record.available_product_ids = False

    @api.depends("section_product_id")
    def _compute_available_attribute_values(self):
        """Compute available attribute values based on selected product."""
        for record in self:
            try:
                if not record.section_product_id:
                    record.available_attribute_values = False
                    continue

                # Search for valid attribute values
                valid_attr_values = (
                    self.env["product.template.attribute.value"]
                    .search(
                        [
                            (
                                "product_tmpl_id",
                                "=",
                                record.section_product_id.product_tmpl_id.id,
                            ),
                            ("ptav_active", "=", True),
                        ]
                    )
                    .mapped("product_attribute_value_id")
                )

                # Assign directly to the field
                record.available_attribute_values = valid_attr_values

                _logger.debug(
                    f"""
                    Available Attributes Computed:
                    - Product: {record.section_product_id.display_name}
                    - Template: {record.section_product_id.product_tmpl_id.display_name}
                    - Attributes Found: {len(valid_attr_values)}
                    - Attribute Names: {', '.join(valid_attr_values.mapped('name'))}
                    """
                )

            except Exception as e:
                _logger.error(
                    f"""
                    Error computing available attributes:
                    - Product: {record.section_product_id.display_name if record.section_product_id else 'N/A'}
                    - Error: {str(e)}
                    - Traceback: {traceback.format_exc()}
                    """
                )
                record.available_attribute_values = False

    @api.onchange("section_product_id", "section_attribute_ids")
    def _onchange_section_data(self):
        """Handle changes in product or attribute selections."""
        self.ensure_one()

        # Skip for summary/final states
        if not self.state or self.state in ["summary", "final"]:
            return

        try:
            # Find existing selection for current state
            current_selection = self.section_selection_ids.filtered(
                lambda x: x.section == self.state
            )

            # Prepare values
            vals = {
                "section_product_id": (
                    self.section_product_id.id if self.section_product_id else False
                ),
                "section_attribute_ids": [(6, 0, self.section_attribute_ids.ids)],
                "price": self._validate_price(
                    self.section_price, field_name="section_price"
                ),
            }

            # Update or create selection
            if current_selection:
                current_selection.write(vals)
            else:
                self.env["wizard.section.selection"].create(
                    {"wizard_id": self.id, "section": self.state, **vals}
                )

            _logger.info(
                f"""
                Section Data Updated:
                - State: {self.state}
                - Product: {self.section_product_id.name if self.section_product_id else 'N/A'}
                - Attributes: {len(self.section_attribute_ids)}
                - Price: {self.section_price}
                - Selection: {'Updated' if current_selection else 'Created'}
                """
            )

        except Exception as e:
            _logger.error(
                f"""
                Error updating section data:
                - State: {self.state}
                - Product: {self.section_product_id.name if self.section_product_id else 'N/A'}
                - Error: {str(e)}
                """
            )

    @api.onchange("state", "laterality")
    def _onchange_state_laterality(self):
        """Handle state and laterality changes."""
        if self.state in ["summary", "final"]:
            self.section_product_id = False
            self.section_attribute_ids = [(5, 0, 0)]
            return

        # Load saved selection if exists
        current_selection = self.section_selection_ids.filtered(
            lambda x: x.section == self.state
        )

        if current_selection:
            self.section_product_id = current_selection.product_id
            self.section_attribute_ids = [(6, 0, current_selection.attribute_ids.ids)]
        else:
            self.section_product_id = False
            self.section_attribute_ids = [(5, 0, 0)]

        return {"domain": {"section_product_id": self._get_product_domain()}}

    @api.model
    def _init_record(self, values):
        """Initialize a new record with proper defaults."""
        defaults = {
            "state": "shell_foundation",
            "laterality": "bilateral",
        }
        return {**defaults, **values}

    @api.onchange("section_product_id")
    def _onchange_section_product_id(self):
        """Update section attributes and price when product changes"""
        self.ensure_one()

        # Clear existing attributes and price
        self.section_attribute_ids = False
        self.section_price = 0.0

        # Exit if no product or in summary/final state
        if not self.section_product_id or self.state in ["summary", "final"]:
            return

        try:
            # Update price first
            self._update_section_price()

            # Get valid attribute values for this product
            valid_attr_values = (
                self.env["product.template.attribute.value"]
                .search(
                    [
                        (
                            "product_tmpl_id",
                            "=",
                            self.section_product_id.product_tmpl_id.id,
                        ),
                        ("ptav_active", "=", True),
                    ]
                )
                .mapped("product_attribute_value_id")
            )

            # Update available attributes
            self.available_attribute_values = valid_attr_values

            _logger.debug(
                f"""
                Product Change:
                - Product: {self.section_product_id.display_name}
                - Template: {self.section_product_id.product_tmpl_id.display_name}
                - Price: {self.section_price}
                - Valid Attributes: {len(valid_attr_values)}
                - Attribute Names: {', '.join(valid_attr_values.mapped('name'))}
                - State: {self.state}
                """
            )

            # Update section selection
            self._update_section_selection()

            # Return domain for attribute selection
            return self._get_attribute_domain(valid_attr_values)

        except Exception as e:
            _logger.error(
                f"""
                Error in product onchange:
                - Product: {self.section_product_id.display_name if self.section_product_id else 'N/A'}
                - State: {self.state}
                - Error: {str(e)}
                - Traceback: {traceback.format_exc()}
                """
            )
            return {
                "warning": {
                    "title": _("Error"),
                    "message": _(
                        "Failed to update product attributes. Please try again."
                    ),
                }
            }

    def _update_section_selection(self):
        """Update the section selection record"""
        selection_vals = {
            "product_id": self.section_product_id.id,
            "attribute_ids": False,  # Clear attributes
            "price": self.section_price,
        }

        current_selection = self.section_selection_ids.filtered(
            lambda x: x.section == self.state
        )

        if current_selection:
            current_selection.write(selection_vals)
        else:
            self.env["wizard.section.selection"].create(
                {"wizard_id": self.id, "section": self.state, **selection_vals}
            )

    def _get_attribute_domain(self, valid_attr_values):
        """Get domain for attribute selection"""
        return {
            "domain": {"section_attribute_ids": [("id", "in", valid_attr_values.ids)]}
        }

    def reset_section(self):
        """Reset selections for the current section."""
        self.ensure_one()
        _logger.info(f"Resetting section '{self.state}' for wizard {self.id}.")

        # Clear current section fields
        self.section_product_id = False
        self.section_attribute_ids = [(5, 0, 0)]

        # Remove section selection
        current_selection = self.section_selection_ids.filtered(
            lambda x: x.section == self.state
        )
        if current_selection:
            current_selection.unlink()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Section Reset"),
                "message": _("Section has been reset successfully."),
                "type": "success",
                "sticky": False,
            },
        }

    def _validate_price(self, value, field_name="price"):
        """Validate and convert price values."""
        try:
            return float(value or 0.0)
        except (ValueError, TypeError):
            _logger.warning(
                f"Invalid price value for {field_name}: {value}. Using 0.0 instead."
            )
            return 0.0

    def _format_monetary(self, amount):
        """Format monetary amount with currency."""
        if not isinstance(amount, (int, float)):
            amount = self._validate_price(amount)
        return self.currency_id.symbol + " " + "{:,.2f}".format(amount)

    @api.depends("section_selection_ids.price")
    def _compute_total_price(self):
        """Compute the total price of all sections."""
        for record in self:
            try:
                total = sum(record.section_selection_ids.mapped("price") or [0.0])
                record.total_price = float(total or 0.0)
            except Exception as e:
                _logger.error(
                    f"""
                    Error computing total price:
                    - Wizard ID: {record.id}
                    - Sections: {record.section_selection_ids.ids}
                    - Error: {str(e)}
                    """
                )
                record.total_price = 0.0

    @api.depends("section_product_id", "section_attribute_ids")
    def _compute_section_price(self):
        """Compute the price for the current section based on product and attributes."""
        for wizard in self:
            if wizard.state in ["summary", "final"]:
                wizard.section_price = 0.0
                continue

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

            # Update or create section selection
            if wizard.section_product_id:
                current_selection = wizard.section_selection_ids.filtered(
                    lambda x: x.section == wizard.state
                )
                if current_selection:
                    current_selection.write(
                        {
                            "product_id": wizard.section_product_id.id,
                            "attribute_ids": [(6, 0, wizard.section_attribute_ids.ids)],
                        }
                    )
                else:
                    self.env["wizard.section.selection"].create(
                        {
                            "wizard_id": wizard.id,
                            "section": wizard.state,
                            "product_id": wizard.section_product_id.id,
                            "attribute_ids": [(6, 0, wizard.section_attribute_ids.ids)],
                        }
                    )

    @api.depends("section_selection_ids.price")
    def _compute_running_total_price(self):
        """Compute running total based on completed sections"""
        for wizard in self:
            if wizard.state in ["summary", "final"]:
                wizard.running_total_price = sum(
                    selection.price for selection in wizard.section_selection_ids
                )
            else:
                # Get ordered list of sections
                configs = self.env["wizard.section.configuration"].search(
                    [], order="sequence"
                )
                section_order = configs.mapped("section_name")
                current_index = (
                    section_order.index(wizard.state)
                    if wizard.state in section_order
                    else -1
                )

                # Sum prices up to current section
                wizard.running_total_price = sum(
                    selection.price
                    for selection in wizard.section_selection_ids
                    if section_order.index(selection.section) <= current_index
                )

    @api.depends("running_total_price")
    def _compute_formatted_total_price(self):
        """Format the running total price."""
        for wizard in self:
            wizard.formatted_total_price = f"${wizard.running_total_price:,.2f}"

    def update_section_data(self, values):
        """Update section data with validation."""
        try:
            # Validate and convert price
            if "price" in values:
                values["price"] = self._validate_price(
                    values.get("price"), field_name="section_price"
                )

            # Update section selection
            if self.state not in ["summary", "final"]:
                current_selection = self.section_selection_ids.filtered(
                    lambda x: x.section == self.state
                )

                selection_vals = {
                    "product_id": values.get("product_id", False),
                    "attribute_ids": values.get("attribute_ids", [(5, 0, 0)]),
                    "price": values.get("price", 0.0),
                }

                if current_selection:
                    current_selection.write(selection_vals)
                else:
                    self.env["wizard.section.selection"].create(
                        {"wizard_id": self.id, "section": self.state, **selection_vals}
                    )

            _logger.info(
                f"""
                Section Data Updated:
                - State: {self.state}
                - Values: {values}
                """
            )

        except Exception as e:
            _logger.error(
                f"""
                Error updating section data:
                - State: {self.state}
                - Values: {values}
                - Error: {str(e)}
                """
            )
            values["price"] = 0.0

        return values

    def _update_section_price(self):
        """Update the price for the current section."""
        self.ensure_one()
        try:
            price = 0.0
            if self.section_product_id:
                price = float(self.section_product_id.list_price or 0.0)

            self.section_price = price

            # Update section selection if exists
            current_selection = self.section_selection_ids.filtered(
                lambda x: x.section == self.state
            )
            if current_selection:
                current_selection.write({"price": price})

        except Exception as e:
            _logger.error(
                f"""
                Error updating section price:
                - Product: {self.section_product_id.name if self.section_product_id else 'N/A'}
                - Error: {str(e)}
                """
            )
            self.section_price = 0.0

    @api.depends(
        "section_selection_ids",
        "section_selection_ids.section_product_id",
        "section_selection_ids.price",
    )
    def _compute_summary(self):
        """Generate a summary of all section selections with prices."""
        for wizard in self:
            try:
                summary_lines = []
                total_price = 0.0

                # Get configurations to ensure proper ordering
                configs = self.env["wizard.section.configuration"].search(
                    [], order="sequence"
                )
                section_order = configs.mapped("section_name")

                # Sort selections according to configuration sequence
                sorted_selections = wizard.section_selection_ids.sorted(
                    key=lambda x: (
                        section_order.index(x.section)
                        if x.section in section_order
                        else float("inf")
                    )
                )

                for selection in sorted_selections:
                    if selection.section_product_id:
                        # Format section name
                        section_display = selection.section.replace("_", " ").title()

                        # Get product info
                        product_name = selection.section_product_id.display_name

                        # Get attribute info if any
                        attribute_names = selection.section_attribute_ids.mapped("name")
                        attribute_text = (
                            f" ({', '.join(attribute_names)})"
                            if attribute_names
                            else ""
                        )

                        # Format price
                        price = self._validate_price(selection.price)
                        price_display = self._format_monetary(price)

                        # Build summary line
                        summary_line = f"{section_display}: {product_name}{attribute_text} - {price_display}"
                        summary_lines.append(summary_line)

                        # Add to total
                        total_price += price

                wizard.summary = (
                    "\n".join(summary_lines)
                    if summary_lines
                    else _("No selections made")
                )
                wizard.summary_total = self._validate_price(total_price)

            except Exception as e:
                _logger.error(
                    f"""
                    Error computing summary:
                    - Wizard ID: {wizard.id}
                    - Error: {str(e)}
                    """
                )
                wizard.summary = _("Error generating summary")
                wizard.summary_total = 0.0

    @api.model
    def default_get(self, fields_list):
        """Initialize default values."""
        res = super().default_get(fields_list)

        defaults = {
            "state": "shell_foundation",
            "laterality": "bilateral",
        }

        for field, value in defaults.items():
            if field in fields_list and field not in res:
                res[field] = value

        _logger.info(
            f"""
            Default Get:
            Fields Requested: {fields_list}
            Final Values: {res}
            State: {res.get('state')}
            Laterality: {res.get('laterality')}
        """
        )

        return res

    def submit_wizard(self):
        """Submit wizard selections and create sale order lines."""
        self.ensure_one()

        # Initial validation
        if not self.sale_order_id:
            raise ValidationError(_("No associated sales order found."))
        if not self.section_data:
            raise ValidationError(_("The wizard contains no selections to submit."))

        _logger.info(
            f"Finalizing submission for Sale Order ID: {self.sale_order_id.id}"
        )
        _logger.debug(f"Section Data: {self.section_data}")

        # Process sections within a savepoint transaction
        with self.env.cr.savepoint():
            self._create_order_lines()

        return self._get_redirect_action()

    def _create_order_lines(self):
        """Create sale order lines for each section."""
        for state, data in self.section_data.items():
            if not self._validate_section_data(state, data):
                continue

            try:
                self._create_single_order_line(state, data)
            except Exception as e:
                _logger.error(
                    f"Error creating sale order line for section {state}: {str(e)}"
                )

    def _validate_section_data(self, state, data):
        """Validate section data before creating order line."""
        product_id = data.get("product_id")
        if not product_id:
            _logger.warning(f"No product found for section {state}. Skipping.")
            return False

        product = self.env["product.product"].browse(product_id)
        if not product.exists():
            _logger.error(f"Product with ID {product_id} does not exist")
            return False

        return True

    def _create_single_order_line(self, state, data):
        """Create a single sale order line for a section."""
        section_price = self._validate_price(state, data.get("section_price", 0.0))
        laterality = data.get("laterality", "N/A")

        description = self._format_line_description(state, laterality, section_price)

        self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order_id.id,
                "product_id": data["product_id"],
                "product_uom_qty": 1,
                "price_unit": section_price,
                "name": description,
            }
        )

    def _format_line_description(self, state, laterality, price):
        """Format the description for the sale order line."""
        return (
            f"{state.replace('_', ' ').title()}:\n"
            f"- Laterality: {laterality}\n"
            f"- Price: ${price:,.2f}"
        )

    def _get_redirect_action(self):
        """Return the redirect action after wizard submission."""
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "res_id": self.sale_order_id.id,
            "view_mode": "form",
            "target": "current",
        }
