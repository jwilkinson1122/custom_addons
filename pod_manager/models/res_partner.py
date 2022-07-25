# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class res_partner(models.Model):
    _inherit = 'res.partner'

    is_patient = fields.Boolean(string='Patient')
    is_staff = fields.Boolean(string=' Staff')
    is_person = fields.Boolean(string="Person")
    is_assistant = fields.Boolean(string=" Assistant")
    is_doctor = fields.Boolean(string="Doctor")
    is_practice = fields.Boolean('Practice')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
