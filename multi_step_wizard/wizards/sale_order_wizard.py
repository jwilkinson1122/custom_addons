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
            ("order_info", "Order Info"),
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
    section_product_id = fields.Many2one(
        "product.product",
        string="Section Product",
        domain=lambda self: self._get_product_domain(),
        help="Product selection for the current section.",
    )
    section_attribute_ids = fields.Many2many(
        "product.attribute.value",
        string="Section Attributes",
        help="Attributes belonging to the selected product.",
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
            record.state_display = record.state.capitalize() if record.state else ""

    state_display = fields.Char(
        string="State Display", compute="_compute_state_display"
    )

    @api.constrains("section_data")
    def _check_section_data(self):
        for record in self:
            if not isinstance(record.section_data, dict):
                _logger.error(f"Invalid section_data detected: {record.section_data}")
                raise ValidationError(_("Section data must be a dictionary"))

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
        if "section_data" not in vals or not isinstance(vals["section_data"], dict):
            vals["section_data"] = {}
        return super().create(vals)

    def write(self, vals):
        if "section_data" in vals and not isinstance(vals["section_data"], dict):
            vals["section_data"] = {}
        return super().write(vals)


    # @api.depends("section_data")
    # def _compute_summary(self):
    #     """Generate a summary of all section selections."""
    #     for wizard in self:
    #         summary_lines = []
    #         for state, data in wizard.section_data.items():
    #             product_name = (
    #                 self.env["product.product"]
    #                 .browse(data.get("product_id"))
    #                 .display_name
    #             )
    #             attributes = ", ".join(
    #                 self.env["product.attribute.value"]
    #                 .browse(data.get("attribute_ids", []))
    #                 .mapped("name")
    #             )
    #             summary_lines.append(
    #                 f"{state.capitalize()}: {product_name} ({attributes})"
    #             )
    #         wizard.summary = "\n".join(summary_lines)

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


    def _get_product_domain(self):
        """Limit products based on the current section and laterality."""
        configuration = self.env["wizard.section.configuration"].search(
            [("section_name", "=", self.state)], limit=1
        )
        domain = [("sale_ok", "=", True)]
        if configuration:
            domain.append(
                ("categ_id", "child_of", configuration.product_category_id.id)
            )

        if self.laterality == "left":
            domain.append(("laterality", "=", "left"))
        elif self.laterality == "right":
            domain.append(("laterality", "=", "right"))
        # No restrictions for bilateral
        return domain

    @api.onchange("section_product_id", "section_attribute_ids", "section_price")
    def _onchange_section_selections(self):
        self._update_section_data()

    @api.onchange("section_product_id")
    def _onchange_section_product_id(self):
        """Limit attributes based on selected product and laterality."""
        if self.section_product_id:
            self.section_attribute_ids = False  # Clear previous selections
            domain = [
                ("product_tmpl_id", "=", self.section_product_id.product_tmpl_id.id)
            ]
            if self.laterality in ["left", "right"]:
                domain.append(("laterality", "=", self.laterality))
            return {"domain": {"section_attribute_ids": domain}}

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
