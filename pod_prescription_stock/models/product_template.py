# -*- coding: utf-8 -*-


from odoo import api, models, fields, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    prescription_delay = fields.Integer(
        'Customer Lead Time', default=0,
        help="Manufacturing lead time, in days. It's the number of days, between the confirmation of the prescription order and the completed product.")

    @api.depends('type')
    def _compute_expense_policy(self):
        super()._compute_expense_policy()
        self.filtered(lambda t: t.type == 'product').expense_policy = 'no'

    @api.depends('type')
    def _compute_service_type(self):
        super()._compute_service_type()
        self.filtered(lambda t: t.type == 'product').service_type = 'manual'
