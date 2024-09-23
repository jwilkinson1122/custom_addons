from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    product_brand_id = fields.Many2one(comodel_name="product.brand", string="Brand")

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["product_brand_id"] = "t.product_brand_id"
        return res

    def _group_by_sale(self):
        group_by = super()._group_by_sale()
        group_by = f"""
            {group_by},
            t.product_brand_id"""
        return group_by
