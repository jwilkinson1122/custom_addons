from odoo import fields, models


class PodiatryQuoteLayoutCategory(models.Model):
    _name = "pod.quote.layout_category"
    _description = "Podiatry Quote Layout Category"
    _order = "sequence, id"

    name = fields.Char("Name", required=True, translate=True)
    sequence = fields.Integer("Sequence", required=True, default=10)
    subtotal = fields.Boolean("Add subtotal", default=True)
    pagebreak = fields.Boolean("Add pagebreak")
    quote_id = fields.Many2one("pod.quote", string="Quote", ondelete="cascade")
