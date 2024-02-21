from datetime import time

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from odoo.tools import float_compare, float_round, float_is_zero


class EmbroideryScarp(models.Model):
    _name = 'embroidery.scrap'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True
    _description = 'embroidery scrap'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    product_id = fields.Many2one('product.product', string='Product', ondelete='restrict')
    origin = fields.Char(string="Source Document", required=False)
    scrap_qty = fields.Float(string="Quantity", required=False, default=1.000)
    company_id = fields.Many2one('res.company', string='Company', required=False, readonly=False,
                                 default=lambda self: self.env.company)
    state = fields.Selection([
        ('draft', 'Draft'), ('done', 'Done'),
    ], compute='_compute_state', string='Status', copy=False, index=True, readonly=True, store=True,
        help="Status of the scrap.", default='draft')

    @api.model
    def create(self, vals):
        # overriding the create method to add the sequence
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('embroidery.scrap') or _('New')
        result = super(EmbroideryScarp, self).create(vals)
        return result

    def action_validate(self):
        self.state = 'done'
