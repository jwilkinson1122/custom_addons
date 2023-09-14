

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    pod_commission = fields.Boolean(string="Podiatry commission", default=False)
