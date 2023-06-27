from odoo import _, api, fields, models


class ProductNomenclature(models.Model):
    _name = "product.nomenclature"
    _description = "Product nomenclature"

    code = fields.Char(required=True)
    name = fields.Text(required=True)
    item_ids = fields.One2many(
        "product.nomenclature.product", inverse_name="nomenclature_id"
    )
    active = fields.Boolean(default=True)

    def action_view_items(self):
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "product_nomenclature." "product_nomenclature_product_action"
        )
        result["context"] = {"default_nomenclature_id": self.id}
        result["domain"] = [("nomenclature_id", "=", self.id)]
        return result


class ProductNomenclatureProduct(models.Model):
    _name = "product.nomenclature.product"
    _description = "Product nomenclature product"

    nomenclature_id = fields.Many2one("product.nomenclature", required=True)
    product_id = fields.Many2one("product.product", required=True)
    code = fields.Char(required=True)
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "product_nomenclature_unique",
            "unique(product_id, nomenclature_id)",
            _("Product must be unique in a nomenclature"),
        )
    ]

    @api.onchange("product_id")
    def _onchange_product(self):
        if not self.name:
            self.name = self.product_id.name
        if not self.code:
            self.code = self.product_id.default_code
