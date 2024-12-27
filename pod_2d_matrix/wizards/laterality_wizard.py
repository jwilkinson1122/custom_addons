from odoo import fields, models


class LateralityWizard(models.TransientModel):
    _name = "podiatry.laterality.wizard"
    _description = "Add Products Based on Laterality"

    laterality = fields.Selection(
        [
            ("left_only", "Left Only"),
            ("right_only", "Right Only"),
            ("bilateral", "Bilateral"),
        ],
        string="Foot Laterality",
        required=True,
    )

    category_id = fields.Many2one(
        "product.category",
        string="Product Category",
        required=True,
    )

    product_ids = fields.Many2many(
        "product.product", string="Products", domain="[('categ_id', '=', category_id)]"
    )

    def add_products_to_matrix(self):
        # Add selected products to the laterality matrix
        active_id = self.env.context.get("active_id")
        sale_order = self.env["sale.order"].browse(active_id)
        matrix_record = sale_order.laterality_matrix.filtered(
            lambda r: r.laterality == self.laterality
            and r.category_id == self.category_id
        )

        if matrix_record:
            matrix_record.product_ids |= self.product_ids
        else:
            self.env["podiatry.laterality.matrix"].create(
                {
                    "order_id": active_id,
                    "laterality": self.laterality,
                    "category_id": self.category_id.id,
                    "product_ids": [(6, 0, self.product_ids.ids)],
                }
            )
