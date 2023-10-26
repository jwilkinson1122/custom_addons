# -*- coding: utf-8 -*-


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    last_prescription_location_id = fields.Many2one('prescription.location')
    favorite_prescription_product_ids = fields.Many2many('prescription.product', 'prescription_product_favorite_partner_rel', 'partner_id', 'product_id')
