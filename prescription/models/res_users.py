# -*- coding: utf-8 -*-


from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    last_prescription_location_id = fields.Many2one('prescription.location')
    favorite_prescription_product_ids = fields.Many2many('prescription.product', 'prescription_product_favorite_user_rel', 'user_id', 'product_id')
