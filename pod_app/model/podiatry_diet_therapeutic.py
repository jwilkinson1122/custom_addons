# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class podiatry_diet_therapeutic(models.Model):
    _name = 'podiatry.diet.therapeutic'
    _description = 'podiatry Diet Therapeutic'

    name = fields.Char(string='Diet Type', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description', required=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
