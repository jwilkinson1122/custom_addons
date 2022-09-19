from odoo import fields, models


class res_partner_reference_type(models.Model):

    _name = 'res.partner.reference.type'
    _description = 'Partner Reference Type'

    name = fields.Char('Name', required=True, translate=True)
    active = fields.Boolean('Active', default=True)
