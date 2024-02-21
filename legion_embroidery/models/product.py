from datetime import time

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class ProductInherit(models.Model):
    _inherit = "product.product"

    partner_id = fields.Many2one('res.partner', string="Brand")
