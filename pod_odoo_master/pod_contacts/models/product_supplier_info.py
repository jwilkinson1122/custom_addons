from odoo import fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    supplier_type_id = fields.Many2one(
        comodel_name="supplier.type",
        related="partner_id.supplier_type_id",
        string="Supplier Type",
    )
