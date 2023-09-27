

from odoo import fields, models


class ProductPodiatryPracticeCompany(models.Model):

    _name = "product.pod.practice.company"
    _description = "Product Template Podiatry Practice Company"  # TODO

    product_tmpl_id = fields.Many2one("product.template", required=True)
    practice_id = fields.Many2one(
        "res.partner",
        domain=[("is_pod", "=", True), ("is_company", "=", True)],
        required=True,
    )
    company_id = fields.Many2one("res.company")

    _sql_constraints = [
        (
            "product_pod_practice_company_unique",
            "unique(product_tmpl_id, practice_id)",
            "This product is already defined for this practice",
        ),
    ]
