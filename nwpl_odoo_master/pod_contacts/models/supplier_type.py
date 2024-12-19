from odoo import models, fields


class SupplierType(models.Model):
    _name = "supplier.type"
    _description = "Supplier Type"

    name = fields.Char(string="Name")
