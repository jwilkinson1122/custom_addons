from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    pod_center_company_ids = fields.One2many(
        "product.pod.center.company",
        inverse_name="product_tmpl_id",
    )
