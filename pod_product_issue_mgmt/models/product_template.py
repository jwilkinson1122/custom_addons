

from odoo import models


class ProductTemplate(models.Model):

    _name = "product.template"
    _inherit = ["product.template", "mgmtsystem.quality.issue.abstract"]


class ProductProduct(models.Model):
    _inherit = "product.product"

    def action_view_quality_issues(self):
        return self.product_tmpl_id.action_view_quality_issues()
