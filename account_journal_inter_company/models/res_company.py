from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    inter_company_ids = fields.One2many(
        comodel_name="res.inter.company", inverse_name="company_id"
    )

    related_company_ids = fields.Many2many(
        comodel_name="res.company", compute="_compute_related_company_ids"
    )

    def _compute_related_company_ids(self):
        for record in self:
            record.related_company_ids = record.inter_company_ids.mapped(
                "related_company_id"
            )
