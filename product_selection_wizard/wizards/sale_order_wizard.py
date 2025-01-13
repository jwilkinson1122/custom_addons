import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class SaleOrderWizard(models.TransientModel):
    _name = "sale.order.wizard"
    _description = "Sale Order Wizard"

    sale_order_id = fields.Many2one(
        "sale.order", default=lambda self: self.env.context.get("active_id")
    )
    total_price = fields.Float(compute="_compute_total_price", string="Total Price")
    section_configurations = fields.One2many(
        "product.section.configuration", compute="_compute_section_configurations"
    )
    section_id = fields.Many2one(
        "product.section.configuration",
        string="Section",
        required=True,
    )
    section_selection_ids = fields.One2many(
        "product.section.selection", "wizard_id", string="Section Selections"
    )
    available_attribute_ids = fields.Many2many(
        "product.attribute.value",
        compute="_compute_available_attributes",
        string="Available Attributes",
    )

    @api.depends("section_selection_ids.product_id")
    def _compute_available_attributes(self):
        """Compute available attributes based on selected products."""
        for record in self:
            product_ids = record.section_selection_ids.mapped("product_id")
            if product_ids:
                attribute_values = self.env["product.template.attribute.value"].search([
                    ("product_tmpl_id", "in", product_ids.mapped("product_tmpl_id").ids)
                ]).mapped("product_attribute_value_id")
                record.available_attribute_ids = attribute_values
            else:
                record.available_attribute_ids = [(5, 0, 0)]

    @api.depends()
    def _compute_section_configurations(self):
        """Fetch all section configurations."""
        for record in self:
            record.section_configurations = self.env["product.section.configuration"].search([], order="sequence")

    @api.depends("section_selection_ids.price")
    def _compute_total_price(self):
        """Compute the total price from all sections."""
        for record in self:
            record.total_price = sum(selection.price for selection in record.section_selection_ids)

    @api.model
    def default_get(self, fields):
        res = super(SaleOrderWizard, self).default_get(fields)
        configurations = self.env["product.section.configuration"].search([], order="sequence")
        section_data = [
            {"wizard_id": self.id, "section_id": config.id}
            for config in configurations
        ]
        res["section_selection_ids"] = [(0, 0, data) for data in section_data]
        return res

    def clear_all(self):
        """Clear all section selections."""
        self.section_selection_ids.unlink()
        self.total_price = 0.0

    def submit_wizard(self):
        """Validate and submit the wizard."""
        required_sections = self.section_configurations.filtered("is_required")
        for config in required_sections:
            if not any(selection.section_id == config for selection in self.section_selection_ids):
                raise ValidationError(_("The section '%s' is required.") % config.description)
        _logger.info(f"Wizard {self.id} submitted successfully.")
        return {"type": "ir.actions.act_window_close"}

class ProductSectionConfiguration(models.Model):
    _name = "product.section.configuration"
    _description = "Product Section Configuration"
    _order = "sequence"

    sequence = fields.Integer(default=10)
    section_id = fields.Char(string="Section Identifier", required=True)
    description = fields.Text(string="Section Description")
    product_category_id = fields.Many2one(
        "product.category", string="Product Category", required=True
    )
    is_required = fields.Boolean(string="Is Required", default=False)
    product_ids = fields.One2many(
        "product.template", "section_id", string="Products", help="Products in this section."
    )

    _sql_constraints = [
        ("unique_section_id", "unique(section_id)", "Section identifier must be unique.")
    ]

    # def name_get(self):
    #     """Customize how the section name is displayed."""
    #     result = []
    #     for record in self:
    #         name = f"{record.description or 'No Description'}"
    #         result.append((record.id, name))
    #     return result
    
    def name_get(self):
        """Customize how the section name is displayed."""
        result = []
        for record in self:
            name = f"[{record.section_id}] {record.description or 'No Description'}"
            result.append((record.id, name))
        return result



class ProductSectionSelection(models.TransientModel):
    _name = "product.section.selection"
    _description = "Product Section Selection"

    wizard_id = fields.Many2one(
        "sale.order.wizard", string="Wizard", required=True, ondelete="cascade"
    )
    section_id = fields.Many2one(
        "product.section.configuration", string="Section", required=True
    )

    section_name = fields.Char(
        string="Section Name", compute="_compute_section_name", store=False
    )

    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=True,
        domain="[('product_tmpl_id', 'in', section_product_ids)]",
    )

    section_product_ids = fields.Many2many(
        "product.template",
        string="Section Products",
        compute="_compute_section_product_ids",
        store=False,  # This is a computed field; no need to store it
    )


    attribute_ids = fields.Many2many(
        "product.attribute.value", string="Attributes", domain="[('id', 'in', available_attribute_ids)]"
    )
    available_attribute_ids = fields.Many2many(
        "product.attribute.value", compute="_compute_available_attributes", store=False
    )
    price = fields.Float(string="Price", compute="_compute_price", store=True)

    @api.depends("section_id")
    def _compute_section_name(self):
        """Compute the section name from the section_id."""
        for record in self:
            record.section_name = record.section_id.description or "Unnamed Section"

    @api.depends("section_id")
    def _compute_section_product_ids(self):
        """Compute the products related to the selected section."""
        for record in self:
            record.section_product_ids = record.section_id.product_ids.ids if record.section_id else []

    @api.depends("product_id")
    def _compute_available_attributes(self):
        """Compute available attributes for the selected product."""
        for record in self:
            if record.product_id:
                ptavs = self.env["product.template.attribute.value"].search([
                    ("product_tmpl_id", "=", record.product_id.product_tmpl_id.id)
                ])
                record.available_attribute_ids = ptavs.mapped("product_attribute_value_id")
            else:
                record.available_attribute_ids = self.env["product.attribute.value"].browse([])

    @api.depends("product_id", "attribute_ids")
    def _compute_price(self):
        """Calculate the price for the selected product and attributes."""
        for record in self:
            product_price = record.product_id.list_price if record.product_id else 0.0
            attribute_extra_price = sum(
                ptav.price_extra for ptav in self.env["product.template.attribute.value"].search([
                    ("product_tmpl_id", "=", record.product_id.product_tmpl_id.id),
                    ("product_attribute_value_id", "in", record.attribute_ids.ids),
                ])
            )
            record.price = product_price + attribute_extra_price
