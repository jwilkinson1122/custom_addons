# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    is_food = fields.Boolean(string='Is Food')
