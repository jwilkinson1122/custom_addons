from odoo import fields, models


class res_partner_reference(models.Model):

    _name = 'res.partner.reference'
    _description = 'Partner Reference'

    reference_type_id = fields.Many2one(
        'res.partner.reference.type', 'Reference Type', required=True)
    value = fields.Char('Value', required=True)
    partner_id = fields.Many2one('res.partner', copy=False)
