from odoo import fields, models


class ProductSet(models.Model):

    _inherit = "product.set"

    typology = fields.Selection(selection=[("set", "Default"), ("instruction", "Instruction")], default="set")
