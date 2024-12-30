from odoo import models, fields


class RestrictMenu(models.Model):
    """ Inherited Menu Items"""
    _inherit = 'ir.ui.menu'

    restrict_user_ids = fields.Many2many('res.users', store=True)
