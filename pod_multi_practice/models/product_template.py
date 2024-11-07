# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    """inherited product"""

    _inherit = "product.template"

    practice_id = fields.Many2one(
        "res.practice",
        string="Practice",
        store=True,
        help="Leave this field empty if this product is"
        " shared between all practices",
    )
    allowed_practice_ids = fields.Many2many(
        "res.practice",
        store=True,
        string="Allowed Practices",
        compute="_compute_allowed_practice_ids",
    )

    @api.depends("company_id")
    def _compute_allowed_practice_ids(self):
        for po in self:
            po.allowed_practice_ids = self.env.user.practice_ids.ids
