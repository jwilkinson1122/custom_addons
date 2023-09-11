from odoo import fields, models


class ProductPodiatryCenterCompany(models.Model):

    _name = "product.pod.center.company"
    _description = "Product Template Podiatry Center Company"  # TODO

    product_tmpl_id = fields.Many2one("product.template", required=True)
    center_id = fields.Many2one(
        "res.partner",
        domain=[("is_pod", "=", True), ("is_center", "=", True)],
        required=True,
    )
    company_id = fields.Many2one("res.company")

    _sql_constraints = [
        (
            "product_pod_center_company_unique",
            "unique(product_tmpl_id, center_id)",
            "This product is already defined for this center",
        ),
    ]
