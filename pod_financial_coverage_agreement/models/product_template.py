

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    include_zero_sales = fields.Boolean(default=False)

    agreement_comment = fields.Text("Agreement Comment")

    def write(self, vals):
        res = super().write(vals)
        if "categ_id" in vals:
            self.env["pod.coverage.agreement.item"].search(
                [("product_id", "in", self.mapped("product_variant_ids").ids)]
            ).write({"categ_id": vals["categ_id"]})
        return res


class ProductProduct(models.Model):
    _inherit = "product.product"

    def write(self, vals):
        res = super().write(vals)
        if "categ_id" in vals:
            self.env["pod.coverage.agreement.item"].search(
                [("product_id", "in", self.ids)]
            ).write({"categ_id": vals["categ_id"]})
        return res
