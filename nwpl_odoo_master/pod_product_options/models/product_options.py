# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class PreconfiguredProduct(models.Model):
    _name = "product.preconfigured"
    _description = "Pre-Configured Product"

    @api.onchange("product_id")
    def product_id_onchange(self):
        return {"domain": {"product_id": [("is_pre_configured", "=", False)]}}

    name = fields.Char("name")
    product_template_id = fields.Many2one("product.template", "Item")
    product_quantity = fields.Float("Quantity", default="1", required=True)
    product_id = fields.Many2one("product.product", "Product", required=True)
    uom_id = fields.Many2one("uom.uom", related="product_id.uom_id")
    price = fields.Float("Product_price")


class ProductOptions(models.Model):
    _name = "product.options"
    _description = "Product Options"
    _order = "prod_tmpl_id, sequence, id"

    def _get_input_type(self):
        return [
            ("field", "Text Field"),
            ("area", "Text Area"),
            ("date", "Date"),
            ("date_time", "Date & Time"),
            ("time", "Time"),
            ("radio", "Radio Button"),
            ("multiple", "Multiple Select"),
            ("checkbox", "Checkbox"),
            ("drop_down", "Dropdown"),
            ("file", "File"),
        ]

    name = fields.Char(
        string="Title",
        help="Title for the product option.",
        required=True,
        translate=True,
    )
    input_type = fields.Selection(
        _get_input_type,
        string="Input Type",
        help="Input type for the product option.",
        required=True,
    )
    is_required = fields.Boolean(
        string="Required", help="Is this a requierd option for this product."
    )
    prod_tmpl_id = fields.Many2one(
        "product.template", string="Product Template", required=True, ondelete="cascade"
    )
    active = fields.Boolean(
        "Active",
        default=True,
        help="If unchecked, it will allow you to hide the option without removing it.",
    )
    sequence = fields.Integer(string="Sequence", default=10)

    price = fields.Float(
        string="Price",
        digits=dp.get_precision("Product Price"),
        help="Price for the product option.",
    )
    product_options_value_ids = fields.One2many(
        "product.options.value",
        "product_option_id",
        string="Product Options Values",
    )

    # File related info
    allowed_file_extension = fields.Char(
        string="Allowed File Extensions",
        help="Comma separated file extensions like jpeg,png.",
    )
    image_size_length = fields.Integer(
        string="Image Length", help="Maximum length allowed for Image."
    )
    image_size_width = fields.Integer(
        string="Image Width", help="Maximum width allowed for Image."
    )

    _sql_constraints = [
        (
            "name_tmpl_uniq",
            "unique(name, prod_tmpl_id, input_type)",
            "Product option names must be unique per product & option type !",
        ),
    ]


class ProductOptionsValue(models.Model):
    _name = "product.options.value"
    _description = "Product Option Values"
    _order = "product_option_id, sequence, id"

    name = fields.Char(
        string="Title",
        help="Title for the product option value.",
        required=True,
        translate=True,
    )
    price = fields.Float(
        string="Price",
        digits=dp.get_precision("Product Price"),
        help="Price for the product option value.",
    )
    product_option_id = fields.Many2one(
        "product.options",
        string="Product Option",
        required=True,
        ondelete="cascade",
    )
    is_default = fields.Boolean(
        string="Default Value", help="Is this a default option for this product."
    )
    sequence = fields.Integer(string="Sequence", default=10)

    _sql_constraints = [
        (
            "name_option_uniq",
            "unique(name, product_option_id)",
            "Product option value names must be unique per option !",
        ),
    ]


class SaleProductOptions(models.Model):
    _name = "sale.product.options"
    _description = "Sales Product Option"

    product_option_id = fields.Many2one(
        "product.options",
        string="Product Option",
        required=True,
        ondelete="restrict",
    )
    order_line_id = fields.Many2one(
        "sale.order.line",
        string="Order Line",
        required=True,
        ondelete="cascade",
        index=True,
    )
    price = fields.Float(
        string="Price",
        digits=dp.get_precision("Product Price"),
        help="Price for the product option value.",
    )
    input_data = fields.Text(string="Input")
    file_data = fields.Binary(string="File Uploaded")
    # file_preview = fields.Binary(related='file_data', string="File Preview")

    def remove(self):
        if self.order_line_id.state in ["cancel", "done"]:
            raise UserError(
                "You can't remove an option when order is Locked or Cancelled."
            )
        orderLineId = self.order_line_id.id
        self.unlink()
        return {
            "name": ("Information"),
            "view_mode": "form",
            "view_type": "form",
            "res_model": "sale.order.line",
            "view_id": self.env.ref(
                "nwpl_odoo_master.sale_order_line_product_options_form"
            ).id,
            "res_id": orderLineId,
            "type": "ir.actions.act_window",
            "nodestroy": True,
            "target": "new",
            "domain": "[]",
        }
