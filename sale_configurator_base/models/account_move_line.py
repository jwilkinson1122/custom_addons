from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("sale_line_ids")
    def _compute_has_parent(self):
        for rec in self:
            rec.has_parent = any([line.parent_id for line in rec.sale_line_ids])

    has_parent = fields.Boolean(compute="_compute_has_parent", store=True)
