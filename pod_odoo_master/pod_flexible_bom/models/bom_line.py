from odoo import fields, models, api


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    unit_cost = fields.Float(string="Unit cost", related="product_id.product_tmpl_id.standard_price")
    total_cost = fields.Float(string="Total cost", compute="_compute_total_cost")
    currency_id = fields.Many2one("res.currency", related="product_id.currency_id")

    @api.depends("product_id", "product_qty")
    def _compute_total_cost(self):
        for record_id in self:
            record_id.total_cost = record_id.product_qty * record_id.unit_cost
