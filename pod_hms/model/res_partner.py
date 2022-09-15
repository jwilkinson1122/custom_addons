# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class res_partner(models.Model):
    _inherit = 'res.partner'

    is_patient = fields.Boolean(string='Patient')
    is_person = fields.Boolean(string="Person")
    is_practitioner = fields.Boolean(string="Practitioner")
    # is_practice = fields.Boolean('Medical Practice')
    is_practice = fields.Boolean(
        "Partner Practice", track_visibility='onchange')

    reference = fields.Char('ID Number')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
