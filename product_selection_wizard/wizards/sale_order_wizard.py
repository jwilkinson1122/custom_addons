import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ProductSectionConfiguration(models.Model):
    _name = "product.section.configuration"
    _description = "Product Section Configuration"
    _order = "sequence"

    sequence = fields.Integer(default=10)
    section_name = fields.Selection(
        selection=lambda self: self.env["sale.order.wizard"]._selection_state(),
        required=True,
    )
    product_category_id = fields.Many2one("product.category", required=True)


class ProductSectionSelection(models.TransientModel):
    _name = "product.section.selection"
    _description = "Product Section Selection"

    wizard_id = fields.Many2one(
        "sale.order.wizard", string="Wizard", required=True, ondelete="cascade"
    )
    section_name = fields.Selection(
        selection=lambda self: self.env["sale.order.wizard"]._selection_state(),
        string="Section Name",
        required=True,
    )
    product_id = fields.Many2one(
        "product.product", string="Product", required=True, ondelete="restrict"
    )
    attribute_ids = fields.Many2many("product.attribute.value", string="Attributes")
    price = fields.Float(string="Price", digits="Product Price", required=True)


class SaleOrderWizard(models.TransientModel):
    _name = "sale.order.wizard"
    _description = "Sale Order Wizard"

    state = fields.Selection(
        selection="_selection_state", default="shell_foundation", required=True
    )
    allow_back = fields.Boolean(compute="_compute_allow_back")
    section_data = fields.Json(
        string="Section Data", default={}, required=False, copy=False
    )
    laterality = fields.Selection(
        [
            ("left", "Left Only"),
            ("right", "Right Only"),
            ("bilateral", "Bilateral"),
        ],
        string="Laterality",
        default="bilateral",
        required=True,
    )
    sale_order_id = fields.Many2one(
        "sale.order", default=lambda self: self.env.context.get("active_id")
    )
    section_product_id = fields.Many2one(
        "product.product", domain="[('id', 'in', available_product_ids)]"
    )
    section_selection_ids = fields.One2many(
        "product.section.selection", "wizard_id", string="Section Selections"
    )
    available_product_ids = fields.Many2many(
        "product.product", compute="_compute_available_products"
    )
    section_attribute_ids = fields.Many2many("product.attribute.value")
    section_price = fields.Float(compute="_compute_section_price")
    total_price = fields.Float(compute="_compute_total_price")
    summary = fields.Text(compute="_compute_summary")

    @api.model
    def _selection_state(self):
        return [
            ("shell_foundation", "Shell / Foundation"),
            ("arch_height", "Arch Height"),
            ("top_cover", "Top Cover"),
            ("bottom_cover", "X-Guard"),
            ("cushion", "Cushion"),
            ("extension", "Extension"),
            ("options", "Options"),
            ("summary", "Summary"),
            ("final", "Final"),
        ]

    @api.depends("state")
    def _compute_allow_back(self):
        for record in self:
            record.allow_back = record.state != "shell_foundation"

    @api.depends("section_product_id", "section_attribute_ids")
    def _compute_section_price(self):
        """Compute the total price for the section, including attribute extra prices."""
        for record in self:
            if not record.section_product_id:
                record.section_price = 0.0
                continue

            # Base price from the product
            base_price = record.section_product_id.list_price or 0.0

            # Calculate extra price for selected attributes
            attribute_extra_price = 0.0
            if record.section_product_id:
                ptav_ids = self.env["product.template.attribute.value"].search(
                    [
                        (
                            "product_tmpl_id",
                            "=",
                            record.section_product_id.product_tmpl_id.id,
                        ),
                        (
                            "product_attribute_value_id",
                            "in",
                            record.section_attribute_ids.ids,
                        ),
                    ]
                )
                attribute_extra_price = sum(ptav.price_extra for ptav in ptav_ids)

            # Total price for the section
            record.section_price = base_price + attribute_extra_price

            if _logger.isEnabledFor(logging.DEBUG):
                _logger.debug(
                    f"""
                    Price Computation:
                    - Product: {record.section_product_id.display_name}
                    - Base Price: {base_price}
                    - Attribute Extra: {attribute_extra_price}
                    - Total Price: {record.section_price}
                    """
                )

    @api.depends("section_selection_ids.price", "section_price")
    def _compute_total_price(self):
        """Compute the total price for all section selections."""
        for record in self:
            record.total_price = (
                sum(selection.price for selection in record.section_selection_ids)
                + record.section_price
            )

    @api.depends("state", "section_selection_ids")
    def _compute_summary(self):
        """Compute a summary of the section selections."""
        for record in self:
            summary_lines = []
            for selection in record.section_selection_ids:
                section_name = selection.section_name.replace("_", " ").title()
                product_name = selection.product_id.name
                summary_lines.append(
                    f"{section_name}: {product_name} - {selection.price}"
                )
            record.summary = "\n".join(summary_lines)

    @api.depends("state")
    def _compute_available_products(self):
        """Compute the available products based on the current state."""
        for record in self:
            configuration = self.env["product.section.configuration"].search(
                [("section_name", "=", record.state)], limit=1
            )
            if configuration:
                record.available_product_ids = self.env["product.product"].search(
                    [("categ_id", "child_of", configuration.product_category_id.id)]
                )
            else:
                record.available_product_ids = self.env["product.product"].browse([])

    @api.onchange("state")
    def _onchange_state(self):
        if self.state:
            self.open_section(self.state)

    @api.onchange("section_product_id", "section_attribute_ids")
    def _onchange_section_product_or_attributes(self):
        self._compute_section_price()
        self._compute_total_price()

    @api.onchange("section_price", "section_selection_ids")
    def _onchange_section_price_or_selections(self):
        self._compute_total_price()

    def open_section(self, section_name):
        """
        Open the specified section by name.
        """
        self._save_section()
        self.state = section_name
        self._load_section()
        return self._reopen_wizard()

    def _save_section(self):
        """
        Save the current section's selections.
        """
        self.ensure_one()
        if not self.id:
            self = self.create(
                {
                    "state": self.state,
                    "sale_order_id": self.sale_order_id.id,
                }
            )

        # if not self.id:
        #     raise ValidationError(_("Wizard record is not properly initialized."))

        selection = self.env["product.section.selection"].search(
            [("wizard_id", "=", self.id), ("section_name", "=", self.state)], limit=1
        )
        if self.section_product_id or self.section_attribute_ids:
            if selection:
                selection.write(
                    {
                        "product_id": self.section_product_id.id,
                        "attribute_ids": [(6, 0, self.section_attribute_ids.ids)],
                        "price": self.section_price,
                    }
                )
            else:
                self.env["product.section.selection"].create(
                    {
                        "wizard_id": self.id,
                        "section_name": self.state,
                        "product_id": self.section_product_id.id,
                        "attribute_ids": [(6, 0, self.section_attribute_ids.ids)],
                        "price": self.section_price,
                    }
                )
        elif selection:
            selection.unlink()

    # def _save_section(self):
    #     """
    #     Save the current section's selections.
    #     """
    #     self.ensure_one()

    #     if not self.id:
    #         self.flush()
    #         self._cr.commit()

    #     selection = self.env["product.section.selection"].search(
    #         [("wizard_id", "=", self.id), ("section_name", "=", self.state)], limit=1
    #     )

    #     if self.section_product_id or self.section_attribute_ids:
    #         if selection:
    #             selection.write(
    #                 {
    #                     "product_id": self.section_product_id.id,
    #                     "attribute_ids": [(6, 0, self.section_attribute_ids.ids)],
    #                     "price": self.section_price,
    #                 }
    #             )
    #         else:
    #             self.env["product.section.selection"].create(
    #                 {
    #                     "wizard_id": self.id,
    #                     "section_name": self.state,
    #                     "product_id": self.section_product_id.id,
    #                     "attribute_ids": [(6, 0, self.section_attribute_ids.ids)],
    #                     "price": self.section_price,
    #                 }
    #             )
    #     elif selection:
    #         selection.unlink()

    def _load_section(self):
        """
        Load selections for the current section.
        """
        _logger.info(f"Loading section for state: {self.state} in wizard {self.id}.")
        self.ensure_one()
        selection = self.env["product.section.selection"].search(
            [("wizard_id", "=", self.id), ("section_name", "=", self.state)], limit=1
        )
        if selection:
            self.section_product_id = selection.product_id
            self.section_attribute_ids = [(6, 0, selection.attribute_ids.ids)]
            self.section_price = selection.price
        else:
            # Reset fields to clean state
            self.section_product_id = False
            self.section_attribute_ids = [(5, 0, 0)]
            self.section_price = 0.0

    def _handle_state_transition(self, direction):
        """
        Handle the state transition for next and previous buttons.
        """
        states = self._get_states()
        current_index = states.index(self.state)
        if direction == "next":
            new_index = min(current_index + 1, len(states) - 1)
        elif direction == "previous":
            new_index = max(current_index - 1, 0)
        self.state = states[new_index]
        self._load_section()
        return self._reopen_wizard()

    def open_next(self):
        """
        Open the next section.
        """
        return self._handle_state_transition("next")

    def open_previous(self):
        """
        Open the previous section.
        """
        return self._handle_state_transition("previous")

    def _get_states(self):
        """
        Get the list of states for the wizard.
        """
        return [
            "shell_foundation",
            "arch_height",
            "top_cover",
            "bottom_cover",
            "cushion",
            "extension",
            "options",
            "summary",
            "final",
        ]

    def _reopen_wizard(self):
        """
        Reopen the wizard to reflect changes.
        """
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }

    def clear_section(self):
        """
        Clear selections for the current section without closing the wizard.
        Includes validation and logging to ensure the operation is robust.
        """
        self.ensure_one()

        # Validate the current state
        if not self.state:
            raise ValidationError(
                _("The wizard is not in a valid state to clear the section.")
            )

        _logger.info(f"Resetting section '{self.state}' for wizard {self.id}.")

        # Fetch existing selections for the current section
        existing_selections = self.env["product.section.selection"].search(
            [("wizard_id", "=", self.id), ("section_name", "=", self.state)]
        )

        if not existing_selections:
            _logger.warning(
                f"No existing selections found to clear for section '{self.state}' in wizard {self.id}."
            )

        # Clear the current selections
        self.section_product_id = False
        self.section_attribute_ids = [(5, 0, 0)]
        self.section_price = 0.0

        # Remove saved selections and handle errors
        try:
            existing_selections.unlink()
            _logger.info(
                f"Cleared saved selections for section '{self.state}' in wizard {self.id}."
            )
        except Exception as e:
            _logger.error(
                f"Error while clearing selections for section '{self.state}' in wizard {self.id}: {str(e)}"
            )
            raise ValidationError(
                _("An error occurred while clearing the section. Please try again.")
            )

        # Reopen the wizard to reflect changes
        return self._reopen_wizard()

    def clear_all(self):
        """
        Clear all sections and restart the wizard from the first section.
        """
        self.ensure_one()

        _logger.info(f"Clearing all sections for wizard {self.id}.")

        # Remove all saved selections
        self.env["product.section.selection"].search(
            [("wizard_id", "=", self.id)]
        ).unlink()

        # Reset the wizard to the initial state
        self.section_product_id = False
        self.section_attribute_ids = [(5, 0, 0)]
        self.section_price = 0.0
        self.state = "shell_foundation"

        return self._reopen_wizard()

    def submit_wizard(self):
        """
        Submit the wizard and finalize the selections.
        """
        self.ensure_one()
        self._save_section()
        _logger.info(f"Submitting wizard {self.id} with final selections.")
        # Implement any additional logic needed for submission
        return {
            "type": "ir.actions.act_window_close",
        }
