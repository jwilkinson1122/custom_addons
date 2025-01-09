import logging
import json
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ProductSelectionWizardMixin(models.AbstractModel):
    _name = "product.selection.wizard.mixin"
    _description = "Product Selection Wizard Mixin"

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

    def _ensure_section_data(self):
        if not isinstance(self.section_data, dict):
            try:
                self.section_data = (
                    json.loads(self.section_data) if self.section_data else {}
                )
            except (ValueError, json.JSONDecodeError):
                self.section_data = {}

    def open_next(self):
        self._ensure_section_data()
        self._handle_state_transition("next")
        return self._reopen_wizard()

    def open_previous(self):
        self._ensure_section_data()
        self._handle_state_transition("previous")
        return self._reopen_wizard()

    def _handle_state_transition(self, direction):
        states = [state[0] for state in self._selection_state()]
        current_index = states.index(self.state)

        if direction == "next" and current_index < len(states) - 1:
            self.state = states[current_index + 1]
        elif direction == "previous" and current_index > 0:
            self.state = states[current_index - 1]
        else:
            raise ValidationError(_("No further state transitions possible."))

    def submit_wizard(self):
        if not self.section_data:
            raise ValidationError("No section data available for submission.")
        self._finalize_submission()

    def _finalize_submission(self):
        raise NotImplementedError("Submission logic must be implemented in subclass")

    def _reopen_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }


class ProductSectionConfiguration(models.Model):
    _name = "product.section.configuration"
    _description = "Product Section Configuration"
    _order = "sequence"

    sequence = fields.Integer(default=10)
    section_name = fields.Selection(
        selection=ProductSelectionWizardMixin._selection_state, required=True
    )
    product_category_id = fields.Many2one("product.category", required=True)


class ProductSectionSelection(models.TransientModel):
    _name = "product.section.selection"
    _description = "Product Section Selection"

    wizard_id = fields.Many2one(
        "sale.order.wizard", string="Wizard", required=True, ondelete="cascade"
    )
    section_name = fields.Selection(
        selection=ProductSelectionWizardMixin._selection_state,
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
    _inherit = "product.selection.wizard.mixin"
    _description = "Sale Order Wizard"

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

            # _logger.debug(
            #     f"""
            #     Price Computation:
            #     - Product: {record.section_product_id.display_name}
            #     - Base Price: {base_price}
            #     - Attribute Extra: {attribute_extra_price}
            #     - Total Price: {record.section_price}
            #     """
            # )

    @api.depends("section_selection_ids.price")
    def _compute_total_price(self):
        for record in self:
            record.total_price = sum(
                selection.price for selection in record.section_selection_ids
            )

    @api.depends("state", "section_selection_ids")
    def _compute_summary(self):
        for record in self:
            summary_lines = []
            for selection in record.section_selection_ids:
                summary_lines.append(
                    f"{selection.section_name}: {selection.product_id.name} - {selection.price}"
                )
            record.summary = "\n".join(summary_lines)

    @api.depends("state")
    def _compute_available_products(self):
        for record in self:
            configuration = self.env["product.section.configuration"].search(
                [("section_name", "=", record.state)], limit=1
            )
            if configuration:
                record.available_product_ids = self.env["product.product"].search(
                    [("categ_id", "child_of", configuration.product_category_id.id)]
                )
            else:
                record.available_product_ids = self.env["product.product"]

    @api.onchange("section_product_id", "section_attribute_ids")
    def _onchange_section_product_or_attributes(self):
        self._compute_section_price()

    # store the current selections for the active section.
    def _save_section(self):
        if self.section_product_id or self.section_attribute_ids:
            # Proceed only if there's valid data to save
            existing_selection = self.env["product.section.selection"].search(
                [("wizard_id", "=", self.id), ("section_name", "=", self.state)],
                limit=1,
            )

            if existing_selection:
                existing_selection.write(
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

    # restore selections for the active section.
    def _load_section(self):
        selection = self.env["product.section.selection"].search(
            [("wizard_id", "=", self.id), ("section_name", "=", self.state)], limit=1
        )
        if selection:
            self.section_product_id = selection.product_id
            self.section_attribute_ids = [(6, 0, selection.attribute_ids.ids)]
        else:
            # Reset fields to clean state
            self.section_product_id = False
            self.section_attribute_ids = [(5, 0, 0)]
            self.section_price = 0.0

    # Override the navigation methods (open_next, open_previous) to save and load data.
    def open_next(self):
        self._save_section()
        self._handle_state_transition("next")
        self._load_section()
        return self._reopen_wizard()

    def open_previous(self):
        self._save_section()
        self._handle_state_transition("previous")
        self._load_section()
        return self._reopen_wizard()

    # Add a "Clear Section" Button
    # Add a button to explicitly clear selections for the current section.
    def clear_section(self):
        """
        Reset selections for the current section.
        Includes validation to ensure the operation is appropriate.
        """
        self.ensure_one()  # Ensure the method is called on a single record

        if not self.state:
            raise ValidationError(
                _("The wizard is not in a valid state to clear the section.")
            )

        _logger.info(f"Resetting section '{self.state}' for wizard {self.id}.")

        # Check if there are existing selections to clear
        existing_selections = self.env["product.section.selection"].search(
            [("wizard_id", "=", self.id), ("section_name", "=", self.state)]
        )

        if not existing_selections:
            _logger.warning(
                f"No existing selections found to clear for section '{self.state}' in wizard {self.id}."
            )
            return  # Exit if there's nothing to clear

        # Confirm that the user wants to clear the section (optional, if supported by UI)
        # Implement UI confirmation here if needed

        # Clear the current selections
        self.section_product_id = False
        self.section_attribute_ids = [(5, 0, 0)]
        self.section_price = 0.0

        # Remove saved selections for the current section
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
