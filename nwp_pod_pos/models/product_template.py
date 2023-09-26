

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    pod_practice_company_ids = fields.One2many(
        "product.pod.practice.company",
        inverse_name="product_tmpl_id",
    )
