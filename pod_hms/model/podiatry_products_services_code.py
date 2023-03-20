# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class podiatry_products_services_code(models.Model):
    _name = 'podiatry.products.services.code'
    _description = 'podiatry products services code'

    name = fields.Char('Code', required=True)
    description = fields.Text('Long Text', required=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
