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

    # Fields
    state = fields.Selection(
        selection="_selection_state", default="shell_foundation", required=True
    )
    allow_back = fields.Boolean(compute="_compute_allow_back")
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
    available_product_ids = fields.Many2many(
        "product.product", compute="_compute_available_products"
    )
    section_attribute_ids = fields.Many2many("product.attribute.value")
    section_price = fields.Float(compute="_compute_section_price", store=True)
    total_price = fields.Float(compute="_compute_total_price", store=True)
    section_selection_ids = fields.One2many(
        "product.section.selection", "wizard_id", string="Section Selections"
    )
    summary = fields.Text(compute="_compute_summary")

    # Selection States
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

    # Compute Methods
    @api.depends("state")
    def _compute_allow_back(self):
        for record in self:
            record.allow_back = record.state != "shell_foundation"

    @api.depends("section_product_id", "section_attribute_ids")
    def _compute_section_price(self):
        """Calculate the section price based on the product and attributes."""
        for record in self:
            if not record.section_product_id:
                record.section_price = 0.0
                continue

            base_price = record.section_product_id.list_price or 0.0
            attribute_extra_price = sum(
                ptav.price_extra
                for ptav in self.env["product.template.attribute.value"].search(
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
            )
            record.section_price = base_price + attribute_extra_price

            _logger.debug(
                f"Computed section price: {record.section_price} "
                f"(Base: {base_price}, Extra: {attribute_extra_price})"
            )

    @api.depends("section_selection_ids", "section_price")
    def _compute_total_price(self):
        for record in self:
            total = sum(selection.price for selection in record.section_selection_ids)
            record.total_price = total + record.section_price
            _logger.debug(f"Total price computed: {record.total_price}")

    @api.depends("section_selection_ids")
    def _compute_summary(self):
        """Generate a summary of all section selections."""
        for record in self:
            record.summary = "\n".join(
                f"{sel.section_name}: {sel.product_id.name} - {sel.price}"
                for sel in record.section_selection_ids
            )

    @api.depends("state")
    def _compute_available_products(self):
        """Determine available products based on the current section configuration."""
        for record in self:
            config = self.env["product.section.configuration"].search(
                [("section_name", "=", record.state)], limit=1
            )
            record.available_product_ids = (
                self.env["product.product"].search(
                    [("categ_id", "child_of", config.product_category_id.id)]
                )
                if config
                else self.env["product.product"].browse([])
            )

    # State Transition Methods
    def open_section(self, section_name):
        """Save the current section and load the specified section."""
        self._save_section()
        self.state = section_name
        self._load_section()

    def _save_section(self):
        """Save the current section selections."""
        self.ensure_one()
        if not self.id:
            self = self.create(
                {"state": self.state, "sale_order_id": self.sale_order_id.id}
            )

        selection = self.env["product.section.selection"].search(
            [
                ("wizard_id", "=", self.id),
                ("section_name", "=", self.state),
            ],
            limit=1,
        )

        if self.section_product_id or self.section_attribute_ids:
            vals = {
                "wizard_id": self.id,
                "section_name": self.state,
                "product_id": self.section_product_id.id,
                "attribute_ids": [(6, 0, self.section_attribute_ids.ids)],
                "price": self.section_price,
            }
            (
                selection.write(vals)
                if selection
                else self.env["product.section.selection"].create(vals)
            )
        elif selection:
            selection.unlink()

    def _load_section(self):
        """Load the saved selection for the current section."""
        selection = self.env["product.section.selection"].search(
            [
                ("wizard_id", "=", self.id),
                ("section_name", "=", self.state),
            ],
            limit=1,
        )
        if selection:
            self.section_product_id = selection.product_id
            self.section_attribute_ids = [(6, 0, selection.attribute_ids.ids)]
            self.section_price = selection.price
        else:
            self.section_product_id = False
            self.section_attribute_ids = [(5, 0, 0)]
            self.section_price = 0.0

    def _reopen_wizard(self):
        """Reopen the wizard to refresh the UI."""
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
        }

    # Wizard Actions
    def open_next(self):
        """Navigate to the next section."""
        states = [state[0] for state in self._selection_state()]
        self.open_section(states[min(states.index(self.state) + 1, len(states) - 1)])

    def open_previous(self):
        """Navigate to the previous section."""
        states = [state[0] for state in self._selection_state()]
        self.open_section(states[max(states.index(self.state) - 1, 0)])

    def clear_section(self):
        """Clear current section selections."""
        self.section_product_id = False
        self.section_attribute_ids = [(5, 0, 0)]
        self.section_price = 0.0
        self.env["product.section.selection"].search(
            [
                ("wizard_id", "=", self.id),
                ("section_name", "=", self.state),
            ]
        ).unlink()

    def clear_all(self):
        """Reset all sections and restart the wizard."""
        self.section_selection_ids.unlink()
        self.state = "shell_foundation"
        return self._reopen_wizard()

    def submit_wizard(self):
        """Finalize and submit the wizard."""
        self._save_section()
        _logger.info(f"Wizard {self.id} submitted successfully.")
        return {"type": "ir.actions.act_window_close"}
