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
    _name = "product.options"
    _description = "CPQ Product Options"
    _rec_name = "display_name"
    _parent_name = "parent_id"
    _parent_store = True
    _order = "display_name asc, sequence"
    # _order = "parent_path, sequence"

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
    is_leaf = fields.Boolean(compute="_compute_is_leaf", store=True, index=True)
    comment = fields.Text()
    active = fields.Boolean(default=True)

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        if self._origin and self._origin.parent_id != self.parent_id:
            return {
                "warning": {
                    "title": _("Warning"),
                    "message": _(
                        "Changing the parent of an option record may"
                        " have unexpected results if this has been"
                        " used on a product.\n"
                        "Recommended action is to archive this option and"
                        " create a new one"
                    ),
                }
            }

    @api.depends("name", "parent_id.display_name")
    def _compute_display_name(self):
        for record in self:
            if record.parent_id:
                record.display_name = f"{record.parent_id.display_name}/{record.name}"
            else:
                record.display_name = record.name

    @api.depends("child_ids")
    def _compute_is_leaf(self):
        for record in self:
            record.is_leaf = len(record.child_ids) < 1

    @api.depends("parent_path")
    def _compute_depth(self):
        for record in self:
            record.depth = (record.parent_path or "").count("/") - 1

    def _compute_child_count(self):
        read_group_res = self.read_group(
            [
                ("parent_id", "child_of", self.ids),
            ],
            ["parent_id"],
            ["parent_id"],
        )
        group_data = {
            data["parent_id"][0]: data["parent_id_count"]
            for data in read_group_res
            if data["parent_id"]
        }
        for record in self:
            child_count = 0
            for sub_parent_id in record.search([("id", "child_of", record.ids)]).ids:
                child_count += group_data.get(sub_parent_id, 0)
            record.child_count = child_count

    def return_final_child_variants(self):
        """Returns child variants that have no child_ids"""
        self.ensure_one()

        return self.search(
            [("parent_path", "ilike", self.parent_path + "%"), ("is_leaf", "=", True)]
        )

    def action_view_children(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "cpq.product_options_action"
        )
        action["domain"] = [
            ("parent_path", "ilike", self.parent_path + "%"),
            ("id", "!=", self.id),
        ]
        action["name"] = "Children"
        return action
    
    @api.constrains("parent_id")
    def _check_option_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_("You cannot create recursive options."))

    # @api.model
    # def create(self, vals):
    #     if vals.get("parent_id") and "sequence" not in vals:
    #         siblings = self.search([("parent_id", "=", vals["parent_id"])])
    #         max_seq = max(siblings.mapped("sequence") or [0])
    #         vals["sequence"] = max_seq + 10

    #     return super().create(vals)

    # def write(self, vals):
    #     if "parent_id" in vals and "sequence" not in vals:
    #         for record in self:
    #             if record.parent_id.id != vals["parent_id"]:
    #                 siblings = self.search([("parent_id", "=", vals["parent_id"])])
    #                 max_seq = max(siblings.mapped("sequence") or [0])
    #                 vals["sequence"] = max_seq + 10

    #     return super().write(vals)
