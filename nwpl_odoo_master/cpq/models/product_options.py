from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class ProductPreconfigured(models.Model):
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
    _inherit = ['avatar.mixin']
    _name = "product.options"
    _description = "Custom Product Options"
    _rec_name = "display_name"
    _parent_name = "parent_id"
    _parent_store = True
    _order = "display_name asc, sequence"
    
    active = fields.Boolean(
        "Active",
        default=True,
        help="If unchecked, it will allow you to hide the option without removing it.",
    )
 
    option_id = fields.Many2one("product.attribute", string="Option Group", required=False)
    
    product_attribute_value_id = fields.Many2one(
        "product.attribute.value",
        string="Linked Product Attribute Value",
        help="Optional direct link to a legacy product.attribute.value for compatibility.",
    )

    name = fields.Char(
        string="Title",
        help="Title for the product option.",
        required=True,
        translate=True,
    )
    sequence = fields.Integer(string="Sequence", default=10)
    description = fields.Text(translate=True)
    display_name = fields.Char(
        compute="_compute_display_name",
        store=True,
        recursive=True,
        index=True,
    )
    parent_id = fields.Many2one(
        comodel_name="product.options", string="Parent", ondelete="cascade"
    )
    parent_path = fields.Char(index=True, unaccent=False)
    depth = fields.Integer(compute="_compute_depth", store=True)
    child_ids = fields.One2many(
        comodel_name="product.options",
        inverse_name="parent_id",
        string="Children",
        domain="[('parent_id', '=', False)]",
    )
    child_count = fields.Integer(compute="_compute_child_count")
    child_badge_info = fields.Char(
        string="Child Badges",
        compute="_compute_child_badge_info",
        store=False
    )
    is_leaf = fields.Boolean(compute="_compute_is_leaf", store=True, index=True)
    code = fields.Char("Internal Code")
    comment = fields.Text()
    active = fields.Boolean(default=True)
    html_color = fields.Char("Color Code", help="Hex or HTML color code (for swatch display)")
    image_128 = fields.Image("Image 128", max_width=128, max_height=128)
    group_label = fields.Char(compute="_compute_group_label", store=True)
    group_order = fields.Integer(compute="_compute_group_order", store=True)
    
    
    # @api.depends("is_leaf")
    # def _compute_group_label(self):
    #     for rec in self:
    #         rec.group_label = "Option" if rec.is_leaf else "Group"

    # @api.depends("is_leaf")
    # def _compute_group_order(self):
    #     for rec in self:
    #         rec.group_order = 0 if not rec.is_leaf else 1

    # @api.onchange("parent_id")
    # def _onchange_parent_id(self):
    #     if self._origin and self._origin.parent_id != self.parent_id:
    #         return {
    #             "warning": {
    #                 "title": _("Warning"),
    #                 "message": _(
    #                     "Changing the parent of an option record may"
    #                     " have unexpected results if this has been"
    #                     " used on a product.\n"
    #                     "Recommended action is to archive this option and"
    #                     " create a new one"
    #                 ),
    #             }
    #         }

    # @api.depends("name", "parent_id.display_name")
    # def _compute_display_name(self):
    #     for record in self:
    #         if record.parent_id:
    #             record.display_name = f"{record.parent_id.display_name}/{record.name}"
    #         else:
    #             record.display_name = record.name

    # @api.depends("child_ids")
    # def _compute_is_leaf(self):
    #     for record in self:
    #         record.is_leaf = len(record.child_ids) < 1

    # @api.depends("parent_path")
    # def _compute_depth(self):
    #     for record in self:
    #         record.depth = (record.parent_path or "").count("/") - 1

    # def _compute_child_count(self):
    #     read_group_res = self.read_group(
    #         [
    #             ("parent_id", "child_of", self.ids),
    #         ],
    #         ["parent_id"],
    #         ["parent_id"],
    #     )
    #     group_data = {
    #         data["parent_id"][0]: data["parent_id_count"]
    #         for data in read_group_res
    #         if data["parent_id"]
    #     }
    #     for record in self:
    #         child_count = 0
    #         for sub_parent_id in record.search([("id", "child_of", record.ids)]).ids:
    #             child_count += group_data.get(sub_parent_id, 0)
    #         record.child_count = child_count

    # def return_final_child_variants(self):
    #     """Returns child variants that have no child_ids"""
    #     self.ensure_one()

    #     return self.search(
    #         [("parent_path", "ilike", self.parent_path + "%"), ("is_leaf", "=", True)]
    #     )

    # def action_view_children(self):
    #     self.ensure_one()
    #     action = self.env["ir.actions.actions"]._for_xml_id(
    #         "nwpl_odoo_master.product_options_action"
    #     )
    #     action["domain"] = [
    #         ("parent_path", "ilike", self.parent_path + "%"),
    #         ("id", "!=", self.id),
    #     ]
    #     action["name"] = "Children"
    #     return action
    
    # @api.constrains("parent_id")
    # def _check_option_recursion(self):
    #     if not self._check_recursion():
    #         raise ValidationError(_("You cannot create recursive options."))

    # @api.depends("child_ids.display_name", "child_ids.is_leaf")
    # def _compute_child_badge_info(self):
    #     for rec in self:
    #         names = [
    #             f"{child.name} (Option)" if child.is_leaf else child.name
    #             for child in rec.child_ids[:10] if child.name
    #         ]
    #         rec.child_badge_info = ", ".join(names)

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

    product_option_id = fields.Many2one(
        "product.options",
        string="Product Option",
        required=True,
        ondelete="cascade",
    )
    is_default = fields.Boolean(
        string="Default Value", help="Is a default option for this product."
    )
    sequence = fields.Integer(string="Sequence", default=10)


