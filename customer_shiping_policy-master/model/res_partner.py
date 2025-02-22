from odoo import models,fields,api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    picking_policy = fields.Selection([
        ('direct', 'As soon as possible'),
        ('one', 'When all products are ready')],
        string='Shipping Policy', required=True, default='direct',
    )

