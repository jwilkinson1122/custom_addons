from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    attribute_set_id = fields.Many2one(
        "attribute.set",
        "Default Attribute Set",
        context={"default_model_id": "product.template"},
    )

    def write(self, vals):
        # Fill Category's products with Category's default attribute_set_id if empty
        super().write(vals)
        for record in self:
            if vals.get("attribute_set_id"):
                templates = self.env["product.template"].search(
                    [("categ_id", "=", record.id), ("attribute_set_id", "=", False)]
                )
                templates.write({"attribute_set_id": record.attribute_set_id.id})
        return True
